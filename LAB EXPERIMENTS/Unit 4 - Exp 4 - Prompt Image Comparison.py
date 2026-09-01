from diffusers import StableDiffusionPipeline
import torch

pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")

prompts = [
    "A modern bridge over a river",
    "A futuristic steel bridge over a river at sunset",
    "A futuristic smart bridge with sensors and vehicles"
]

for i, prompt in enumerate(prompts, 1):
    image = pipe(prompt).images[0]
    image.save(f"prompt_image_{i}.png")
    print(f"Saved prompt_image_{i}.png")
