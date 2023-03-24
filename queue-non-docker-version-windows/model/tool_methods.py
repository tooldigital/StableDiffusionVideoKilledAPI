import torch
import gc
import os
import time
import numpy as np
import shutil
from PIL import Image, ImageOps
import requests
from io import BytesIO
from tqdm import tqdm
from time import sleep
import random

from diffusers import (
    StableDiffusionPipeline,
    StableDiffusionImg2ImgPipeline,
    StableDiffusionDepth2ImgPipeline,
    PNDMScheduler,
    LMSDiscreteScheduler,
    DDIMScheduler,
    EulerDiscreteScheduler,
    EulerAncestralDiscreteScheduler,
    DPMSolverMultistepScheduler,
)

txt_to_img_pipe = None
img_to_img_pipe = None
dpth_to_img_pipe = None

def getImageForPrompt(_prompt, _neg,_width, _height,_steps,_guidance,_seed,_scheduler,_samples,_selectedmodel):

  global txt_to_img_pipe

  if _seed == 0:
    _seed = random.randint(0, 2147483647)

  print("***********************")
  print("CREATING IMAGE")
  print("MODEL: "+_selectedmodel)
  print("SCHEDULER: "+_scheduler)
  print("PROMPT: "+_prompt)
  print("SEED: "+str(_seed))

  txt_to_img_pipe = StableDiffusionPipeline.from_pretrained(_selectedmodel, torch_dtype=torch.float16)  
  txt_to_img_pipe = txt_to_img_pipe.to("cuda")
  #txt_to_img_pipe.safety_checker = dummy
  if _scheduler == "PNDMScheduler":
    txt_to_img_pipe.scheduler = PNDMScheduler.from_config(txt_to_img_pipe.scheduler.config)
  elif _scheduler == "LMSDiscreteScheduler":
    txt_to_img_pipe.scheduler = LMSDiscreteScheduler.from_config(txt_to_img_pipe.scheduler.config)
  elif _scheduler == "DDIMScheduler":
    txt_to_img_pipe.scheduler = DDIMScheduler.from_config(txt_to_img_pipe.scheduler.config)
  elif _scheduler == "EulerDiscreteScheduler":
    txt_to_img_pipe.scheduler = EulerDiscreteScheduler.from_config(txt_to_img_pipe.scheduler.config)
  elif _scheduler == "EulerAncestralDiscreteScheduler":
    txt_to_img_pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(txt_to_img_pipe.scheduler.config)
  elif _scheduler == "DPMSolverMultistepScheduler":
    txt_to_img_pipe.scheduler = DPMSolverMultistepScheduler.from_config(txt_to_img_pipe.scheduler.config)

  generator = torch.Generator('cuda').manual_seed(_seed)
  images = txt_to_img_pipe(_prompt, negative_prompt=_neg, num_inference_steps=_steps,height=_height, width=_width, guidance_scale=_guidance,generator=generator,num_images_per_prompt=_samples).images
  del txt_to_img_pipe    
  gc.collect()
  torch.cuda.empty_cache()
  return images

def getImageToImageForPrompt(_image,_prompt, _neg,_steps,_strength,_guidance,_seed,_scheduler,_samples,_selectedmodel):
  
  global img_to_img_pipe

  if _seed == 0:
    _seed = random.randint(0, 2147483647)

  print("***********************")
  print("CREATING IMAGE TO IMAGE")
  print("MODEL: "+_selectedmodel)
  print("SCHEDULER: "+_scheduler)
  print("PROMPT: "+_prompt)
  print("SEED: "+str(_seed))
  img_to_img_pipe = StableDiffusionImg2ImgPipeline.from_pretrained(_selectedmodel, torch_dtype=torch.float16)  
  img_to_img_pipe = img_to_img_pipe.to("cuda")
  #img_to_img_pipe.safety_checker = dummy
  if _scheduler == "PNDMScheduler":
    img_to_img_pipe.scheduler = PNDMScheduler.from_config(img_to_img_pipe.scheduler.config)
  elif _scheduler == "LMSDiscreteScheduler":
    img_to_img_pipe.scheduler = LMSDiscreteScheduler.from_config(img_to_img_pipe.scheduler.config)
  elif _scheduler == "DDIMScheduler":
    img_to_img_pipe.scheduler = DDIMScheduler.from_config(img_to_img_pipe.scheduler.config)
  elif _scheduler == "EulerDiscreteScheduler":
    img_to_img_pipe.scheduler = EulerDiscreteScheduler.from_config(img_to_img_pipe.scheduler.config)
  elif _scheduler == "EulerAncestralDiscreteScheduler":
    img_to_img_pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(img_to_img_pipe.scheduler.config)
  elif _scheduler == "DPMSolverMultistepScheduler":
    img_to_img_pipe.scheduler = DPMSolverMultistepScheduler.from_config(img_to_img_pipe.scheduler.config)
  
  generator = torch.Generator('cuda').manual_seed(_seed)
  images = img_to_img_pipe(_prompt, negative_prompt=_neg, image=_image, strength=_strength, guidance_scale=_guidance, num_inference_steps=_steps,generator=generator,num_images_per_prompt=_samples).images
  del img_to_img_pipe    
  gc.collect()
  torch.cuda.empty_cache()
  return images

def getDepthToImage(_image,_prompt, _neg,_steps,_strength,_guidance,_seed,_scheduler,_samples):
  global dpth_to_img_pipe
  print("***********************")
  print("CREATING IMAGE")
  print("MODEL: "+"stabilityai/stable-diffusion-2-depth")
  print("SCHEDULER: "+_scheduler)
  print("PROMPT: "+_prompt)
  print("SEED: "+str(_seed))
  dpth_to_img_pipe = StableDiffusionDepth2ImgPipeline.from_pretrained("stabilityai/stable-diffusion-2-depth", torch_dtype=torch.float16)  
  dpth_to_img_pipe = dpth_to_img_pipe.to("cuda") 
  generator = torch.Generator('cuda').manual_seed(_seed)
  #images = dpth_to_img_pipe(prompt=_prompt, image=_image, negative_prompt=_neg, strength=_strength)
  images = dpth_to_img_pipe(_prompt, negative_prompt=_neg, image=_image, strength=_strength, guidance_scale=_guidance, num_inference_steps=_steps,generator=generator,num_images_per_prompt=_samples).images
  del dpth_to_img_pipe    
  gc.collect()
  torch.cuda.empty_cache()
  return images

