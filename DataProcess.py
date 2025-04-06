"""
Use Qwen API to filter data
"""


import os
from openai import OpenAI
import base64
from PIL import Image
import pillow_avif  
from tqdm import tqdm
import re
import cv2
import numpy as np
import glob
import shutil

def encode_image(image_list):
        base64Images = []
        for imagePath in image_list:
            with open(imagePath, "rb") as image_file:
                base64Images.append(base64.b64encode(image_file.read()).decode("utf-8"))
        return base64Images   

def deleteImages(imageFiles):
    """Delete images"""
    for imageFile in tqdm(imageFiles):
        try:
            prefix = os.path.splitext(imageFile)[0]
            path1 = os.path.join("D:\Model_Data\Datasets\\video_dressup\clothesJPG", f'{prefix}_*.jpg')
            path2 = os.path.join("D:\Model_Data\Datasets\\video_dressup\modelsJPG", imageFile)
            path1 = glob.glob(path1)[0]
            os.remove(path1)
            os.remove(path2)
        except:
            print(f"Error when delete file: {imageFile}")
            exit()
        
def Avif2JPEG(inputFolder, outputFolder):
    """Transfer avif to jpeg"""
    
    for avifName in tqdm(os.listdir(inputFolder)):
        inputFile = os.path.join(inputFolder, avifName)
        outputFile = os.path.join(outputFolder, avifName)
        try:
            img = Image.open(inputFile)
            img = img.convert("RGB")
            img.save(outputFile, "JPEG", quality=95)
        except Exception as e:
            print(f"Error when transfer: {inputFile}\n{e}")

def FilterImages(client, image_list, prompt, 
                 sys_cloth=None, sys_image=None, sys_prompt=None):
    """Use LLM to filter images"""
    # System prompt
    if sys_prompt==None:
        systext = "You are a helpful assistant, please answer only 'yes' or 'no' based on the user's question."
        sysContent = [{"type": "text", "text": systext}]
    else:
        # Images
        base64Images = encode_image([sys_cloth, sys_image])
        systext = sys_prompt
        sysContent = []
        for base64Image in base64Images:
            sysContent.append(
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64Image}"}})
        sysContent.append({"type": "text", "text": systext})


    # User prompt
    # Images
    base64Images = encode_image(image_list)
    userContent = []
    for base64Image in base64Images:
        userContent.append(
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64Image}"}}
        )
    userContent.append({"type": "text", "text": prompt})   
    
    # Call LLM
    completion = client.chat.completions.create(
        model="qwen-vl-max-latest",
        messages=[
            {
                "role": "system",
                "content": sysContent,},
            {
                "role": "user",
                "content": userContent,
            }
        ],
    )
    
    return completion.choices[0].message.content.lower()

def Filter(client, imageFolder, clothesFolder):
    """Filter all images"""
    castModel = []
    castNumber = []
    castInner = []
    upper = []
    lower = []
    whole = []
    
    demoImage = "D:\Code\crawler\demo_model.jpg"
    demoCloth = "D:\Code\crawler\demo_cloth.jpg"
    # index = 0
    for file in tqdm(os.listdir(imageFolder)):
        imageFile = os.path.join(imageFolder, file)
        clothesFile = os.path.join(clothesFolder, file)
        
        # Filter0: Model
        # imageFile = "D:\Model_Data\Datasets\\video_dressup\modelsJPG\\000173.jpg" # debug
        # prompt = "Is there a model in the picture?"
        # answer = FilterImages(client, [imageFile], prompt)
        # if answer in ['no', 'no.']:
        #     castModel.append(file)
        
        # Filter1: Number
        # prompt = "Is the number of clothing items in the image greater than one?"
        # answer = FilterImages(client, [clothesFile], prompt)
        # if answer in ["yes", "yes."]:
        #     castNumber.append(file)
                
        # # Filter2: Inner or not?
        # prompt = "Is the clothing in the first picture the inner layer worn by the model in the second picture?"
        # demoPrompt = "You are a helpful assistant. Now, you are given an image recognition task. Determine whether the clothing in the first image is covered by other clothing in the second image. For example, in the current case, the black T-shirt in the first image is covered by a coat in the second image. Similarly, based on this instruction, check whether the clothing in the first image is covered in the second image for future inputs. Your response should be either 'Yes' or 'No' only."
        # answer = FilterImages(client, [clothesFile, imageFile], prompt, sys_cloth=demoCloth, sys_image=demoImage, sys_prompt=demoPrompt)
        # if answer in ['yes', 'yes.']:
        #     castInner.append(file)
        
        # Annotation
        prompt = "Please determine whether the clothing in the first image, as seen in the second image, belongs to the upper body (e.g., T-shirt), lower body (e.g., shorts), or whole body (e.g., dress). I need your response to be only 'upper body', 'lower body', or 'whole body'."
        answer = FilterImages(client, [clothesFile, imageFile], prompt)
        if answer in ['upper body', 'upper body.']:
            upper.append(file)
        elif answer in ['lower body', 'lower body.']:
            lower.append(file)
        else:
            whole.append(file)
        
        # index += 1
        # if (index+1)%100 == 0:
        #     with open("upper.txt", "w", encoding="utf-8") as file:
        #         if upper != None:
        #             for item in upper:
        #                 file.write(str(item) + "\n")  
        #     with open("lower.txt", "w", encoding="utf-8") as file:
        #         if lower != None:
        #             for item in lower:
        #                 file.write(str(item) + "\n")  
        #     with open("whole.txt", "w", encoding="utf-8") as file:
        #         if whole != None:
        #             for item in whole:
        #                 file.write(str(item) + "\n")   
        
    castIndexList = list(set(castNumber + castInner + castModel))
    return castIndexList, castModel, castNumber, castInner, upper, lower, whole
    
def Rename():
    """Rename files"""
    txts = [
        "D:\\Code\\crawler\\upper.txt",
        "D:\\Code\\crawler\\lower.txt",
        "D:\\Code\\crawler\\whole.txt"
    ]
    
    for kinds, txtFile in enumerate(txts):
        with open(txtFile, 'r', encoding='utf-8') as txt:
            files = txt.readlines()

        files = [file.strip() for file in files if file.strip()]
        for file in files:
            oldFile = os.path.join("D:\Model_Data\Datasets\\video_dressup\clothesJPG", file)
            # New name
            oldName, ext = os.path.splitext(file)  
            newName = f"{oldName}_{kinds+1}{ext}"  
            newFile = os.path.join("D:\Model_Data\Datasets\\video_dressup\clothesJPG", newName)
            if os.path.exists(oldFile):      
                try:
                    os.rename(oldFile, newFile)
                except Exception as e:
                    print(f"Failed to rename {oldFile}: {e}")
            else:
                print(f"Path does not exist: {oldFile}")

def reorder_cloth_dataset(directory):
    """Reorder clothes dataset"""
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    
    pattern = re.compile(r"(\d{6})_(\d)(\.\w+)")
    
    matched_files = []
    for file in files:
        match = pattern.match(file)
        if match:
            base_number, suffix_number, extension = match.groups()
            matched_files.append((int(base_number), int(suffix_number), extension, file))
    
    if not matched_files:
        print("No matching files found.")
        return
    
    matched_files.sort(key=lambda x: (x[0], x[1])) 
    
    new_files = []
    current_number = 0
    for _, suffix_number, extension, old_file in matched_files:
        new_base_number = f"{current_number:06d}"
        new_filename = f"{new_base_number}_{suffix_number}{extension}"
        new_files.append((old_file, new_filename))
        current_number += 1
    
    for old_file, new_file in new_files:
        old_path = os.path.join(directory, old_file)
        new_path = os.path.join(directory, new_file)
        try:
            os.rename(old_path, new_path)
            print(f"Renamed: {old_file} -> {new_file}")
        except Exception as e:
            print(f"Failed to rename {old_file}: {e}")

def reorder_model_dataset(directory):
    """Reorder images datasets"""
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    
    pattern = re.compile(r"(\d{6})(\.\w+)")
    
    matched_files = []
    for file in files:
        match = pattern.match(file)
        if match:
            base_number, extension = match.groups()
            matched_files.append((int(base_number), extension, file))

    if not matched_files:
        print("No matching files found.")
        return

    matched_files.sort(key=lambda x: x[0]) 

    new_files = []
    current_number = 0  
    for _, extension, old_file in matched_files:
        new_base_number = f"{current_number:06d}"  
        new_filename = f"{new_base_number}{extension}"
        new_files.append((old_file, new_filename))
        current_number += 1

    for old_file, new_file in new_files:
        old_path = os.path.join(directory, old_file)
        new_path = os.path.join(directory, new_file)
        try:
            os.rename(old_path, new_path)
            print(f"Renamed: {old_file} -> {new_file}")
        except Exception as e:
            print(f"Failed to rename {old_file}: {e}")

def WhiteFilter(imageFolder):
    """Caculate images with white border"""
    white_threshold = 240  
    check_width = 5  
    count = 0
    fileNames = []
    for filename in tqdm(os.listdir(imageFolder)):
        img_path = os.path.join(imageFolder, filename)
        img = cv2.imread(img_path)

        if img is None:
            continue

        left_border = img[:, :check_width]
        right_border = img[:, -check_width:]

        is_left_white = np.all(left_border > white_threshold)
        is_right_white = np.all(right_border > white_threshold)

        if is_left_white or is_right_white:
            count += 1
            fileNames.append(filename)

    print(f"Number: {count} / {len(os.listdir(imageFolder))}")
    return fileNames
    
def Classify(imageFolder):
    """Classify images"""
    clothesFolder = os.path.join(imageFolder, "clothesJPG")
    modelsFolder = os.path.join(imageFolder, "modelsJPG")
    
    for imageFile in tqdm(os.listdir(clothesFolder)):
        index = imageFile[-5]
        prefix = os.path.splitext(imageFile)[0][:-2]
        
        path1 = os.path.join(clothesFolder, imageFile)
        path2 = os.path.join(modelsFolder, prefix+".jpg")
        
        if index == '1':
            saveFolder = "D:\Model_Data\Datasets\\video_dressup\\upper"
        elif index == '2':
            saveFolder = "D:\Model_Data\Datasets\\video_dressup\\lower"
        else:
            saveFolder = "D:\Model_Data\Datasets\\video_dressup\\dress"
            
        shutil.copy(path1, os.path.join(saveFolder, "clothes"))
        shutil.copy(path2, os.path.join(saveFolder, "images"))
        # Rename
        os.rename(os.path.join(saveFolder, "images", prefix+".jpg"), os.path.join(saveFolder, "images", imageFile))
        
def OrderRename(imageFolder):
    """Rename files in ordered"""
    count = 0
    block = ["upper", "lower", "dress"]
    for index, b in enumerate(block):
        clothesFolder = os.path.join(imageFolder, b, "clothes")
        imagesFolder = os.path.join(imageFolder, b, "images")
        imagesNewFolder = os.path.join(imageFolder, b, "images_new")
        clothesNewFolder = os.path.join(imageFolder, b, "clothes_new")
        
        for imageFile in os.listdir(clothesFolder):
            os.rename(os.path.join(imagesFolder, imageFile), os.path.join(imagesNewFolder, '{:06d}_{:01d}.jpg'.format(count, index+1)))
            os.rename(os.path.join(clothesFolder, imageFile), os.path.join(clothesNewFolder, '{:06d}_{:01d}.jpg'.format(count, index+1)))
            count += 1


if __name__ == '__main__':
    OrderRename("D:\Model_Data\Datasets\\video_dressup")


    exit()
    client = OpenAI(
        api_key="sk-13034cf952fc46e68e008a3569ae2094",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    imageFolder = "D:\Model_Data\Datasets\\video_dressup\modelsJPG"
    clothesFolder = "D:\Model_Data\Datasets\\video_dressup\clothesJPG"
    castIndexList, castModel, castNumber, castInner, upper, lower, whole = Filter(client, imageFolder, clothesFolder)

    
    # # Filter
    # with open("cast.txt", "w", encoding="utf-8") as file:
    #     if castIndexList != None:
    #         for item in castIndexList:
    #             file.write(str(item) + "\n")  
    # with open("castNumber.txt", "w", encoding="utf-8") as file:
    #     if castNumber != None:
    #         for item in castNumber:
    #             file.write(str(item) + "\n")  
    # with open("castInner.txt", "w", encoding="utf-8") as file:
    #     if castInner != None:
    #         for item in castInner:
    #             file.write(str(item) + "\n")  
    # with open("castModel.txt", "w", encoding="utf-8") as file:
    #     if castModel != None:
    #         for item in castModel:
    #             file.write(str(item) + "\n")  
    
    # Annotation       
    with open("upper.txt", "w", encoding="utf-8") as file:
        if upper != None:
            for item in upper:
                file.write(str(item) + "\n")  
    with open("lower.txt", "w", encoding="utf-8") as file:
        if lower != None:
            for item in lower:
                file.write(str(item) + "\n")  
    with open("whole.txt", "w", encoding="utf-8") as file:
        if whole != None:
            for item in whole:
                file.write(str(item) + "\n")       
    

