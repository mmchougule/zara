from PIL import Image, ImageDraw, ImageFont
import io
from typing import Dict
import requests
import replicate
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ImageGenerator:
    async def create_meme(self, concept: str, visual_elements: Dict) -> str:
        """Create meme image from concept"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        try:
            viz_elements = str(visual_elements).replace("'", '"')
            # use replicate to generate image
            input = {
                "prompt": concept + " meme\n\nvisual_elements: " + viz_elements,
                "guidance": 3.5
            }
            output = replicate.run(
                "black-forest-labs/flux-dev",
                input=input
            )
            # Save the generated image
            with open(f'output-{timestamp}.png', 'wb') as f:
                f.write(output[0].read())
            meme_image = ''
            for text in output:
                # print(text, end="")
                meme_image = text
            print(f"Image saved as output-{timestamp}.png and {meme_image}")
            return meme_image
            
        except Exception as e:
            logger.error(f"Error creating meme: {e}", exc_info=True)
            return None