import os

import cv2
import imutils
from django.shortcuts import redirect, render
from PIL import Image
from skimage.metrics import structural_similarity

from setup import settings as app

from .forms import EnviarImagemForm

# Adding path to config
up = 'base_static/uploads'
original = 'base_static/original'
generate = 'base_static/generated'

def index(request):
    form = EnviarImagemForm()   

    if request.method == 'POST':
        form = EnviarImagemForm(request.POST, request.FILES)
        if form.is_valid():
            file_upload = request.FILES['arquivo']
            
            # Resize and save the uploaded image
            uploaded_image = Image.open(file_upload).resize((250,160))
            uploaded_image.save(os.path.join(up, 'image.jpg'))

            # Resize and save the original image to ensure both uploaded and original matches in size
            original_image = Image.open(os.path.join(original, 'image.jpg')).resize((250,160))
            original_image.save(os.path.join(generate, 'image.jpg'))

            # Read uploaded and original image as array
            original_image = cv2.imread(os.path.join(original, 'image.jpg'))
            uploaded_image = cv2.imread(os.path.join(up, 'image.jpg'))

            # Convert image into grayscale
            original_gray = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
            uploaded_gray = cv2.cvtColor(uploaded_image, cv2.COLOR_BGR2GRAY)

            # Calculate structural similarity
            (score, diff) = structural_similarity(original_gray, uploaded_gray, full=True)
            diff = (diff * 255).astype("uint8")

            # Calculate threshold and contours
            thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
    
            # Draw contours on image
            for c in cnts:
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(original_image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.rectangle(uploaded_image, (x, y), (x + w, y + h), (0, 0, 255), 2)

            # Save all output images (if required)
            cv2.imwrite(os.path.join(generate, 'image_original.jpg'), original_image)
            cv2.imwrite(os.path.join(generate, 'image_uploaded.jpg'), uploaded_image)
            cv2.imwrite(os.path.join(generate, 'image_diff.jpg'), diff)
            cv2.imwrite(os.path.join(generate, 'image_thresh.jpg'), thresh)
            result = str(round(score*100,2)) + '%' + ' Parecido'
            
            context = {
                'result': result,
                
            }

            return render(request, 'index.html', context)
        
        else:
            return redirect('home')


	
                      
    else:        
        form = EnviarImagemForm(request.POST, request.FILES)
    return render(request, 'index.html', {'form': form})
