import tool_methods
import random
from PIL import Image, ImageDraw, ImageFont,ImageOps
import redis
import os
import json
import time
import base64
from io import BytesIO
import textwrap
import shutil
from prefetch_generator import BackgroundGenerator
from subprocess import Popen, PIPE
from itertools import cycle
import numpy as np
import imageio
import subprocess
from tqdm import tqdm
import re

pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
db = redis.Redis(connection_pool=pool)
db.ping() 
print("MODEL STARTED")

n_variations = 4
keyframe_images=[]
add_caption = False 
render_key_frames_only = True
my_array = []
inm_images=[]

def add_caption2image(
      image, 
      caption, 
      text_font='LiberationSans-Regular.ttf', 
      font_size=20,
      fill_color=(255, 255, 255),
      stroke_color=(0, 0, 0), #stroke_fill
      stroke_width=2,
      align='center',
      ):
    # via https://stackoverflow.com/a/59104505/819544
    wrapper = textwrap.TextWrapper(width=50) 
    word_list = wrapper.wrap(text=caption) 
    caption_new = ''
    for ii in word_list[:-1]:
        caption_new = caption_new + ii + '\n'
    caption_new += word_list[-1]

    draw = ImageDraw.Draw(image)

    # Download the Font and Replace the font with the font file. 
    font = ImageFont.truetype(text_font, size=font_size)
    w,h = draw.textsize(caption_new, font=font, stroke_width=stroke_width)
    W,H = image.size
    x,y = 0.5*(W-w),0.90*H-h
    draw.text(
        (x,y), 
        caption_new,
        font=font,
        fill=fill_color, 
        stroke_fill=stroke_color,
        stroke_width=stroke_width,
        align=align,
    )
    return image

def process_sequence(idx):
  #return images for this id
  all_frames = []
  keyframe = keyframe_images[idx]
  if(add_caption):
    keyframe = add_caption2image(keyframe, my_array[idx]['prompt']) 
  all_frames.append(keyframe)

  if render_key_frames_only == False:
    startframe = idx+((n_variations*idx)-idx)
    for x in range(n_variations):
      mm_image = inm_images[x+startframe]
      if(add_caption):
        mm_image = add_caption2image(mm_image, my_array[idx]['prompt']) 
      all_frames.append(mm_image)
  
  return all_frames

def generateSD():

    global keyframe_images
    global my_array
    global inm_images
    global add_caption
    global render_key_frames_only
    global n_variations

    while True:

        '''list = db.lrange(os.environ.get("SD_QUEUE"), 0, 0)
        for l in list:
            l = json.loads(l.decode("utf-8"))
            id = l["id"]
            print(id)
            time.sleep(0.5)
            db.set(id, json.dumps({"done":id}))
        '''
       
        # Pop off multiple images from Redis queue atomically
        with db.pipeline() as pipe:
            pipe.lrange("sd_queue", 0, 0)
            pipe.ltrim("sd_queue", 1, -1)
            queue, _ = pipe.execute()

        imageIDs = []
        sd_objects = []
        my_array = []
        inm_images = []
        keyframe_images=[]
        
        for q in queue:
            # Deserialize the object and obtain the input image
            q = json.loads(q.decode("utf-8"))
            obj = {"prompt": q['prompt'],"timings": q['timings'],"negative_prompt":q['negative_prompt'],"steps":q['steps'],"seed":q['seed'],"guidance":q['guidance'],"scheduler":q['scheduler'],"selected_model":q['selected_model'],"strength":q['strength'],"captions":q['captions'],"keyframes":q['keyframes'],"variations":q['variations'],"frames":q['frames'],"fps":q['fps']}
            sd_objects.append(obj)
            # Update the list of image IDs
            imageIDs.append(q["id"])

        # Check to see if we need to process the batch
        if len(imageIDs) > 0:
        
            for id in imageIDs:
                
                add_caption = sd_objects[0]['captions']

                render_key_frames_only = sd_objects[0]['keyframes']

                n_variations=sd_objects[0]['variations']
                strength=sd_objects[0]['strength']
                
                fps = sd_objects[0]['fps']
                video_duration = sd_objects[0]['frames']
                
                prompts = []
                res = re.findall(r'"(.*?)"', q['prompt'])
                for _prompt in res:
                    prompts.append(_prompt)

                times = []
                times = q['timings'].split(",")
                times = [ int(x) for x in times ]
            
                #generate keyframes
                for idx, rec in enumerate(prompts):
                    my_array.append({'ts': times[idx],'prompt':rec})
                
                for idx, rec in enumerate(my_array):
                    lyric = rec['prompt']
                    prompt = f"{lyric}"
                    init_image =  tool_methods.getImageForPrompt(prompt,sd_objects[0]['negative_prompt'],512,512,sd_objects[0]['steps'],sd_objects[0]['guidance'],0,sd_objects[0]['scheduler'],1,sd_objects[0]['selected_model'])[0]
                    keyframe_images.append(init_image)


                ifps = 1/fps
                #max_frames = fps * video_duration

                # dummy prompt for last scene duration
                my_array.append({'ts':video_duration})

                # make sure we respect the duration of the previous phrase
                frame_start=0
                my_array[0]['anim_start']=frame_start
                for i, rec in enumerate(my_array[1:], start=1):
                    rec_prev = my_array[i-1]
                    k=0
                    while (rec_prev['anim_start'] + k*ifps) < rec['ts']:
                        k+=1
                    k-=1
                    rec_prev['frames'] = k
                    rec_prev['anim_duration'] = k*ifps
                    frame_start+=k*ifps
                    rec['anim_start']=frame_start

                # drop the dummy frame
                my_array = my_array[:-1]
               
                if render_key_frames_only == False:
                    for idx,rec in enumerate(my_array):
                        for x in range(n_variations):
                            #_image,_prompt, _neg,_steps,_strength,_guidance,_seed,_scheduler,_samples,_selectedmodel
                            inm_frame = tool_methods.getImageToImageForPrompt(keyframe_images[idx],rec['prompt'],sd_objects[0]['negative_prompt'],sd_objects[0]['steps'],strength,sd_objects[0]['guidance'],0,sd_objects[0]['scheduler'],1,sd_objects[0]['selected_model'])[0]
                            inm_images.append(inm_frame)
                else:
                    print("***********************")
                    print("WE ARE IN KEYFRAME RENDERMODE ONLY")

                batch_gen = BackgroundGenerator(
                [(idx, rec, process_sequence(idx))
                    for idx, rec in enumerate(my_array)]
                ,max_prefetch=2)

                writer = imageio.get_writer("../api/static/"+id+".mp4", fps=fps)
                for idx, rec, batch in tqdm(batch_gen, total=len(my_array)):
                    frame_factory = cycle(batch)
                    k = 0
                    while k < rec['frames']:
                        im = next(frame_factory)
                        I = np.asarray(im)
                        writer.append_data(I)
                        k+=1
                writer.close()

                #image = tool_methods.getImageForPrompt(sd_objects[0]['prompt'],sd_objects[0]['negative_prompt'],512,512,sd_objects[0]['steps'],sd_objects[0]['guidance'],0,sd_objects[0]['scheduler'],1,sd_objects[0]['selected_model'])[0]
                #output =  BytesIO()
                #image.save(output, format="JPEG")
                db.set(id, str(id+".mp4"))
                #output.close()
                time.sleep(0.25)


        # Sleep for a small amount
        time.sleep(0.05)

if __name__ == "__main__":
    generateSD()