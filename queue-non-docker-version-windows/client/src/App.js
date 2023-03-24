import {
  ChakraProvider,
  Heading,
  Container,
  Text,
  Input,
  Button,
  Stack,
  Spinner,
  Select,
  Textarea,
  Checkbox
} from "@chakra-ui/react";

import {
  FormControl,
  FormLabel,
} from "@chakra-ui/form-control"

import {
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
} from '@chakra-ui/react'

import {
  ListItem,
  UnorderedList,
} from '@chakra-ui/react'
import { SimpleGrid } from '@chakra-ui/react'
import { Box } from '@chakra-ui/react'

import axios from "axios";
import { useState } from "react";

const App = () => {

  const [video, updateVideo] = useState('');
  const [timings, updateTimings] = useState('0,15');
  const [prompt, updatePrompt] = useState('"A quirky band formed through their love for music and The Goonies movie","They started with small shows which eventually grew to larger venues, collaborating with established artists along the way"');
  const [neg_prompt, updateNegPrompt] = useState("ugly,duplicate, mutilated, out of frame,  mutation, blurry, bad anatomy, extra legs,low resolution,disfigured");
  const [selected_model, updateSelectedModel] = useState("runwayml/stable-diffusion-v1-5");
  const [selected_scheduler, updateSelectedScheduler] = useState("PNDMScheduler");
  const [guidance, updateGuidance] = useState(7.5);
  const [seed, updateSeed] = useState(0);
  const [strength, updateStrength] = useState(0.5);
  const [steps, updateSteps] = useState(50);
  const [captions, updateCaptions] = useState(false);
  const [keyframes, updateKeyframes] = useState(true);
  const [variations, updateVariations] = useState(4);
  const [frames, updateFrames] = useState(30);
  const [fps, updateFPS] = useState(12);
  const [loading, updateLoading] = useState(false);
  const [error, updateError] = useState(false);
  const [errorMessage, updateErrorMessage] = useState("error");

  const parse = (val) => val.replace(/^\$/, '')

  const checkError = () => {

    var result = false;

    if (!prompt) {
      updateErrorMessage("no prompt defined");
      result = true;
    } else if (!selected_model) {
      updateErrorMessage("no model defined");
      result = true;
    } else if (!selected_scheduler) {
      updateErrorMessage("no scheduler defined");
      result = true;
    } else if (!guidance) {
      updateErrorMessage("no guidance");
      result = true;
    } else if (!steps) {
      updateErrorMessage("no steps");
      result = true;
    } else if (!seed && seed !== 0) {
      updateErrorMessage("no seed");
      result = true;
    }
    return result;
  }

  const generate = async (prompt) => {
    if (checkError()) {
      updateError(true);
    } else {
      updateError(false);
      updateLoading(true);
      const config = {
        headers:{
          "ngrok-skip-browser-warning": "69420"
        }
      };
      const result = await axios.get(`https://489a-78-21-57-225.eu.ngrok.io/generatevideo?prompt=${prompt}&timings=${timings}&negative_prompt=${neg_prompt}&steps=${steps}&seed=${seed}&guidance=${guidance}&scheduler=${selected_scheduler}&selected_model=${selected_model}&strength=${strength}&captions=${captions}&keyframes=${keyframes}&variations=${variations}&frames=${frames}&fps=${fps}`,config);
      updateVideo('https://489a-78-21-57-225.eu.ngrok.io/static/'+result.data);
      updateLoading(false);
    }
  };

  return (
    <ChakraProvider>
      <Container maxW='1080px'>
        <Heading>Tool of North America - Stable Diffusion Video Generator🚀</Heading>

        <Box marginTop={"10px"} marginBottom={"10px"} bg='black' color='white' p={4} borderWidth='1px' borderRadius='lg' >VIDEO KILLED THE RADIOSTAR</Box>

        <Text>We provide 4 base models and other custom models.</Text>
        <Text marginBottom={"10px"}>When using custom model, include this prefix in the prompt</Text>
        <UnorderedList marginBottom={"30px"}>
          <ListItem>wimvanhenden/ultimate-country-v1: <b>ultmtcntry</b></ListItem>
          <ListItem>prompthero/openjourney <b>mdjrny-v4 style</b></ListItem>
          <ListItem>nitrosocke/Arcane-Diffusion: <b>arcane style</b></ListItem>
        </UnorderedList>

         <Text>Prompts</Text>
          <Textarea  placeholder='' value={prompt} onChange={(e) => updatePrompt(e.target.value)}></Textarea>
          
          <Text>Video duration in seconds</Text>
          <NumberInput value={frames} precision={0} step={1} min={1} onChange={(valueString) => updateFrames(parse(valueString))}><NumberInputField /><NumberInputStepper><NumberIncrementStepper /><NumberDecrementStepper /></NumberInputStepper></NumberInput>
       
          <Text>Timings</Text>
          <Textarea  placeholder='' value={timings} onChange={(e) => updateTimings(e.target.value)}></Textarea>

          <Text>Negative prompt</Text>
          <Input placeholder='negative prompt' value={neg_prompt} onChange={(e) => updateNegPrompt(e.target.value)}></Input>

          <FormControl>
            <FormLabel>Model</FormLabel>
            <Select placeholder='runwayml/stable-diffusion-v1-5' value={selected_model} onChange={(e) => updateSelectedModel(e.target.value)} >
              <option>runwayml/stable-diffusion-v1-5</option>
              <option>wimvanhenden/ultimate-country-v1</option>
              <option>nitrosocke/Arcane-Diffusion</option>
              <option>prompthero/openjourney</option>
            </Select>
          </FormControl>

          <FormControl>
            <FormLabel>Scheduler</FormLabel>
            <Select placeholder='PNDMScheduler' value={selected_scheduler} onChange={(e) => updateSelectedScheduler(e.target.value)} >
              <option>PNDMScheduler</option>
              <option>LMSDiscreteScheduler</option>
              <option>DDIMScheduler</option>
              <option>EulerDiscreteScheduler</option>
              <option>EulerAncestralDiscreteScheduler</option>
              <option>DPMSolverMultistepScheduler</option>
            </Select>
          </FormControl>
    
        <SimpleGrid marginBottom={"10px"} columns={8} spacing={0}>
          <Text>Guidance:</Text>
          <Text>Steps:</Text>
          <Text>Seed:</Text>
          <Text>strength:</Text>
          <Text paddingLeft={"10px"}>Captions:</Text>
          <Text paddingLeft={"10px"}>Keyframes only:</Text>
          <Text>Variations:</Text>
          <Text>FPS:</Text>
          <NumberInput value={guidance} precision={2} step={0.1} onChange={(valueString) => updateGuidance(parse(valueString))} ><NumberInputField /><NumberInputStepper><NumberIncrementStepper /><NumberDecrementStepper /></NumberInputStepper></NumberInput>
          <NumberInput value={steps} precision={0} step={1} onChange={(valueString) => updateSteps(parse(valueString))} ><NumberInputField /><NumberInputStepper><NumberIncrementStepper /><NumberDecrementStepper /></NumberInputStepper></NumberInput>
          <NumberInput value={seed} precision={0} step={1} onChange={(valueString) => updateSeed(parse(valueString))} ><NumberInputField /><NumberInputStepper><NumberIncrementStepper /><NumberDecrementStepper /></NumberInputStepper></NumberInput>
          <NumberInput value={strength} precision={2} step={0.1} min={0} max={1} onChange={(valueString) => updateStrength(parse(valueString))}><NumberInputField /><NumberInputStepper><NumberIncrementStepper /><NumberDecrementStepper /></NumberInputStepper></NumberInput>
          <Checkbox paddingLeft={"10px"} isChecked={captions}  onChange={(e) => updateCaptions(e.target.checked)} ></Checkbox>
          <Checkbox paddingLeft={"10px"} isChecked={keyframes}  onChange={(e) => updateKeyframes(e.target.checked)} ></Checkbox>
          <NumberInput value={variations} precision={0} step={1} min={1} onChange={(valueString) => updateVariations(parse(valueString))}><NumberInputField /><NumberInputStepper><NumberIncrementStepper /><NumberDecrementStepper /></NumberInputStepper></NumberInput>
          <NumberInput value={fps} precision={0} step={1} min={1} onChange={(valueString) => updateFPS(parse(valueString))}><NumberInputField /><NumberInputStepper><NumberIncrementStepper /><NumberDecrementStepper /></NumberInputStepper></NumberInput>
    
        </SimpleGrid>

        <Button onClick={(e) => generate(prompt)} marginBottom={"50px"} >Generate</Button>

        {error ? (<Box marginTop={"10px"} marginBottom={"10px"} bg='black' color='white' p={4} borderWidth='1px' borderRadius='lg' >ERROR: {errorMessage}</Box>) : null}

        {loading ? (<Stack><Spinner marginBottom={"50px"} size='xl' /></Stack>) :  video ? (<Box marginBottom={"50px"} as='video' controls src={video} poster='https://cdn.8thwall.com/web/accounts/icons/50z1f4gsobku6ce5aer2xb87wirfmecatq1raz6ttnj0t7cmwi31zupd-400x400' alt='video' objectFit='contain' sx={{aspectRatio: '1/1'}}/>) : null}

      </Container>
    </ChakraProvider>
  );
};

export default App;