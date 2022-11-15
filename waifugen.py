import torch
from torch import autocast
from diffusers import StableDiffusionPipeline, DDIMScheduler

model_id = "hakurei/waifu-diffusion"
device = "cuda"


pipe = StableDiffusionPipeline.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    revision="fp16",
    scheduler=DDIMScheduler(
        beta_start=0.00085,
        beta_end=0.012,
        beta_schedule="scaled_linear",
        clip_sample=False,
        set_alpha_to_one=False,
    ),
)
pipe = pipe.to(device)

prompt = "touhou alice_zuberg 1girl solo portrait"
    
image = pipe(prompt, guidance_scale=7.5)["sample"][0]  
    
image.save("reimu_hakurei.png")