#from ffmeg_tools import ffmpeg_merge_video_audio
from moviepy.editor import *
import time
import time
import re
from ReadEmail import main as mailinfo
from ReadEmail import DebugYN as debug
from PIL import Image 
from moviepy.video.io.ffmpeg_tools import ffmpeg_merge_video_audio
from concurrent.futures import ProcessPoolExecutor

duration_intro = 3.135

def main():
    start = time.time()
    EmailInfoList = mailinfo()
    #AskUserInput()
    for CompanyInfo in EmailInfoList:
        video_list = DetermineVideoList(CompanyInfo['selected_videos'])
        AskUserInput()
        for video in video_list:
            clip = VideoFileClip(video[0])
            text_clips = AddText(clip, CompanyInfo)
            clip = AddTextClips(clip, text_clips)
            clip = AddLogo(clip, CompanyInfo)
            clip = AddGradient(clip, CompanyInfo, video[1])
            print(CompanyInfo)
            WriteVideo(clip, CompanyInfo, video[2])
            end = time.time()
            clip.close()
    print(f"---elapsed time is: {end-start} seconds---")

def DetermineVideoList(videos):
    video_list = []
    for video in videos:
        if video == 1:
            video_list.append(['Template_V1.mp4', 223.21, 1])
        if video == 2:
            video_list.append(['Template_V2.mp4', 87, 2])
        if video == 3:
            video_list.append(['Template_V3.mp4', 103.19, 3])

    return video_list
def AskUserInput():
    user_input = input("Do you want to continue? Please remind to make the logo's transparent (Y/N): ").lower()

    if user_input == "y":
        print("continuing")
        
        # Add your code here for the actions to be taken if the user wants to continue
    elif user_input == "n":
        print("Exiting...")
        sys.exit()
    else:
        print("Invalid input. Please enter 'Y' or 'N'.")
        # Call the function again to ask for input until a valid response is received
        AskUserInput()



def DetermineEndDurationGradient():
    return 8

def AddGradient(clip, CompanyInfo, end_duration):
    gradient_width = clip.size[0]/6
    gradient_height = 131
    duration = end_duration - duration_intro
    text_clips = [clip]

    gradient_bar = AddGradientBar(clip, duration, gradient_width, gradient_height)
    text_clips.append(gradient_bar)
    x_coordinate_img, y_coordinate_img = GetGradientImgCoordinates(clip.size, gradient_bar.size, gradient_width, gradient_height)
    text_clips.append(MakeTitle(CompanyInfo, duration, "white", (26, 612)).set_start(duration_intro))
    text_clips.append(MakeContactGradient(CompanyInfo, duration))
    text_clips.append(AddLogoGradient(CompanyInfo, duration, gradient_width, gradient_height, x_coordinate_img, y_coordinate_img))
    clip = CompositeVideoClip(text_clips)
    
    return clip
def AddLogoGradient(CompanyInfo, duration, width, height, x,y):
    ResizeLogo(CompanyInfo['logo_path'], height, width)
    image_clip = ImageClip("resized_image.png")
    image_clip = SetGradientDuration(image_clip, duration)
    x = x + ((width - image_clip.size[0]) / 2)
    y = y + ((height - image_clip.size[1]) / 2)
    image_clip = image_clip.set_position((x, y))
    image_clip.close()
    return image_clip

def GetGradientImgCoordinates(video_size, clip_size, width, height):
    x = video_size[0] - clip_size[0]
    y = video_size[1] - clip_size[1]
    center_x = x + width / 2
    center_y = y + height / 2
    return x,y

def MakeContactGradient(CompanyInfo, duration):
    contact_text = TextClip(f"Contact us: {CompanyInfo['company_phone']} | {CompanyInfo['company_email']}",font='Segoe-UI-bold', color="white", fontsize=25)
    contact_text = contact_text.set_position((26, 662))
    contact_text = SetGradientDuration(contact_text, duration)
    contact_text.close()
    return contact_text
def SetGradientDuration(textclip, duration):
    textclip = textclip.set_duration(duration)
    textclip = textclip.set_start(duration_intro)
    return textclip

def AddLogo(clip : VideoFileClip, CompanyInfo, start = 0, duration = duration_intro, height = 400, width = 600,x_coordinate = 'center', y_coordinate = "top"):
    ResizeLogo(CompanyInfo['logo_path'], height, width)
    image_clip = ImageClip("resized_image.png")
    image_clip = image_clip.set_duration(duration)
    image_clip = image_clip.set_start(start)
    
    image_clip = image_clip.set_position((x_coordinate, y_coordinate))
    image_clip.close()
    clip = CompositeVideoClip([clip, image_clip])
    return clip
def AddGradientBar(clip, duration, gradient_width, gradient_height):
    # Create a black gradient bar
    gradient_bar = TextClip(
        "a",
        color="black",
        size=(gradient_width, gradient_height),
        bg_color="grey",
        transparent=True,  # Use (0, 0, 0, 0) for transparent background
        fontsize=1,
    )

    # Set the alpha (transparency) of the gradient bar to 0.7 (70%)
    gradient_bar = gradient_bar.set_opacity(0.7)
    gradient_bar = GradientPosition(gradient_bar)
    gradient_bar = SetGradientDuration(gradient_bar, duration)
    return gradient_bar

def GradientPosition(gradient_bar):
    gradient_bar = gradient_bar.set_position(("right", "bottom"))
    return gradient_bar
def ResizeLogo(logo, height, width):
    # Open the image
    img = Image.open(logo)

    # Get the original width and height
    original_width, original_height = img.size

    # Calculate the scaling factors for width and height
    width_ratio = width / original_width
    height_ratio = height / original_height

    # Choose the minimum scaling factor to fit the entire image into the box
    min_ratio = min(width_ratio, height_ratio)

    # Calculate the new width and height
    new_width = int(original_width * min_ratio)
    new_height = int(original_height * min_ratio)

    # Resize the image
    resized_img = img.resize((new_width, new_height))
    try:
        resized_img.save("resized_image.png")
    except:
        resized_img.save("resized_image.jpg")


def AddTextClips(clip, text_clips):
    clip = CompositeVideoClip(text_clips)
    return clip
def WriteVideo(clip, CompanyInfo, video = '1'):
    folder_name= CompanyInfo["company_name"]
    filename = f"In2Care_V{video}_{folder_name.replace(' ', '_')}.mp4"
    output_path = os.path.join(folder_name, filename)
    clip.write_videofile(filename, codec="h264_nvenc", audio_codec="aac", threads=12, fps=24, logger=None, verbose=False)
def AddText(clip, CompanyInfo):
    text_clips =[clip]
    text_clips= AddTextIntro(clip, CompanyInfo, text_clips)
    duration = clip.duration
    return text_clips

def MakeAddress(text, duration, color, position):
    address = TextClip(text,font='Segoe-UI', color=color, fontsize=20)
    address = address.set_position(position)
    address = address.set_duration(duration)
    address.close()
    return address

def AddTextIntro(clip, CompanyInfo, text_clips):
    title_position = (56, 540)
    if 'address' in CompanyInfo:
        title_position = (56, 438)
        i = -1
        for line in CompanyInfo['address']:
            i+=1
            address = MakeAddress(line, duration_intro, color="black", position=(56, 477 + 30 * i))
            text_clips.append(address)
    title = MakeTitle(CompanyInfo, duration_intro, title_color="black", position=title_position)
    text_clips.append(title)
    text_clips = MakeContactUs(CompanyInfo, duration_intro, text_clips)
    return text_clips

def MakeContactUs(CompanyInfo, duration, text_clips):
    y_coordinate = 580
    contact_us = TextClip("Contact us:",font='Segoe-UI-bold', color="black", fontsize=20)
    contact_us = contact_us.set_position((56, y_coordinate))
    contact_us = contact_us.set_duration(duration)
    contact_us.close()
    text_clips.append(contact_us)
    
    distance_between = 30
    text_clips.append(contact_us_text(CompanyInfo['company_phone'], duration, text_clips, y_coordinate+distance_between))
    text_clips.append(contact_us_text(CompanyInfo['company_email'], duration, text_clips, y_coordinate+distance_between*2))
    text_clips.append(contact_us_text(CompanyInfo['website'], duration, text_clips, y_coordinate+distance_between*3))
    return text_clips

def contact_us_text(text, duration, text_clips, y_coordinate):
    contact_us = TextClip(text,font='Segoe-UI', color="black", fontsize=22)
    contact_us = contact_us.set_position((56, y_coordinate))
    contact_us = contact_us.set_duration(duration)
    contact_us.close()
    return contact_us


def MakeTitle(CompanyInfo, duration, title_color, position):
    contact_us = TextClip(CompanyInfo['company_name'],font='Segoe-UI-bold', color=title_color, fontsize=30)
    contact_us = contact_us.set_position(position)
    contact_us = contact_us.set_duration(duration)
    contact_us.close()
    return contact_us
main()