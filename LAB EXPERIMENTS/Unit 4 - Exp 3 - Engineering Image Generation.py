from diffusers import StableDiffusionPipeline
import torch

prompt = input("Enter an engineering image prompt: ")
pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")
image = pipe(prompt).images[0]
image.save("engineering_generated_image.png")
print("Image saved successfully.")
