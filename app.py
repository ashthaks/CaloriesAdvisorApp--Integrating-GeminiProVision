# importing libraries needed
import gradio as gr
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
import tempfile
import imagecodecs

# to load all the environment variables
load_dotenv()  
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

## Function to load Google Gemini Pro Vision API And get response

def get_gemini_repsonse(input,image,prompt):
    model=genai.GenerativeModel('gemini-pro-vision')
    response=model.generate_content([input,image[0],prompt])
    return response.text

def check_uploaded_image(uploaded_img):
    # Check if image has been uploaded
    if uploaded_img is not None:
        # Convert AVIF to JPEG (or PNG) if needed
        if uploaded_img.format != "JPEG":
            temp_filename = tempfile.NamedTemporaryFile(delete=False, suffix='.jpeg')
            uploaded_img.save(temp_filename.name, format="JPEG")
            with open(temp_filename.name, 'rb') as f:
                image_bytes = f.read()
            os.unlink(temp_filename.name)  # Delete the temporary file
        else:
            # If already JPEG, just read the bytes
            with BytesIO() as output:
                uploaded_img.save(output, format='JPEG')
                image_bytes = output.getvalue()

        img_parts = [
            {
                "mime_type": 'image/jpeg',  # MIME type for JPEG images
                "data": image_bytes
            }
        ]
        return img_parts
    else:
        raise FileNotFoundError("No file uploaded")


input_prompt="""
You are an expert in nutritionist where you need to see the food items from the image
               and calculate the total calories, also provide the details of every food items with calories intake
               is below format

               1. Item 1 - no of calories
               2. Item 2 - no of calories
               ----
               ----
Finally you can also mention whether the food is healthy or not and also mention the percentage split of the ratio of 
Carbohydrates, fats, fibres, sugar and other important things required in our diet.

"""

# gradio interface setup

def display_image(img):

    image_data=check_uploaded_image(img)
    response= get_gemini_repsonse(input_prompt,image_data,"")
    return response

description = "Identify the food items from the image and calculate the total calories, also provide the details of every food items with calories intake"
examples = [["pasta.jpeg", " "]]
# Define the theme dictionary
theme = gr.themes.Default(primary_hue="green").set(
    button_primary_background_fill="*primary_200",
    button_primary_background_fill_hover="*primary_300",
)
js = """
function createGradioAnimation() {
    var container = document.createElement('div');
    container.id = 'gradio-animation';
    container.style.fontSize = '2em';
    container.style.fontWeight = 'bold';
    container.style.textAlign = 'center';
    container.style.marginBottom = '20px';

    var text = 'Calories Advisor App!';
    for (var i = 0; i < text.length; i++) {
        (function(i){
            setTimeout(function(){
                var letter = document.createElement('span');
                letter.style.opacity = '0';
                letter.style.transition = 'opacity 0.5s';
                letter.innerText = text[i];

                container.appendChild(letter);

                setTimeout(function() {
                    letter.style.opacity = '1';
                }, 50);
            }, i * 250);
        })(i);
    }

    var gradioContainer = document.querySelector('.gradio-container');
    gradioContainer.insertBefore(container, gradioContainer.firstChild);

    return 'Animation created';
}
"""
app=gr.Interface(
    fn= display_image,
    inputs=gr.Image(type="pil"),
    outputs="text",
    description=description,
    examples=examples,
    submit_btn="Calculate the total calories",
    theme=theme,
    js=js
    )
app.launch()