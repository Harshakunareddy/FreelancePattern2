import shutil
import os
import io
import turtle
import random
import time
import cv2
from PIL import Image
import numpy as np
import mysql.connector
import configparser

# Read configuration from config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

# Database parameters
db_params = {
    'host': config['Database']['host'],
    'user': config['Database']['user'],
    'password': config['Database']['password'],
    'database': config['Database']['database'],
}

# Animation parameters
max_frames = int(config['Animation']['max_frames'])
num_sparkles = int(config['Animation']['num_sparkles'])
frame_delay = float(config['Animation']['frame_delay'])
#video_speed =  float(config['Animation']['video_speed'])
resolution_x = int(config['Animation']['resolution_x'])
resolution_y = int(config['Animation']['resolution_y'])


# Video parameters
output_video_file = config['Video']['output_video_file']
output_images_folder = config['Video']['output_images_folder']

# Color options
#sparkle_colors = config['Colors']['sparkle_colors'].split(', ')



try:
    bgcolor = tuple(map(int, config['Colors']['bgcolor'].split(',')))
except ValueError:
    bgcolor = config['Colors']['bgcolor']

    



# Shape options
sparkle_shapes = config['Shapes']['sparkle_shapes'].split(', ')
shape_size_min = float(config['Shapes']['min'])
shape_size_max = float(config['Shapes']['max'])


#text
text_x = int(config['Text']['x'])
text_y = int(config['Text']['y'])

try:
    text_color = tuple(map(int, config['Text']['color'].split(',')))
except ValueError:
    text_color = config['Text']['color']


text_size = config['Text']['size']




# Set up the screen
screen = turtle.Screen()
screen.title("Sparkles")
screen.tracer(0)


# Fetch text content from MySQL table
def fetch_text_content():
    connection = mysql.connector.connect(**db_params)
    cursor = connection.cursor()

    query = "SELECT text_content FROM text ;"
    cursor.execute(query)
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result[0] if result else "Some random Text"

# Draw the text content at the top of the image
def draw_text_content(text_content):

    turtle.penup()

    turtle.goto(text_x,text_y)  
    turtle.pendown()
    turtle.color(text_color)
    turtle.write(text_content, align="center", font=("Arial",text_size), move=False)
    turtle.hideturtle()

# Function to create a sparkle
def create_sparkle():
   
    sparkle = turtle.Turtle()       
    sparkle.shape(random.choice(sparkle_shapes))


    red_x = int(config['Hexacode']['red_x'])
    red_y = int(config['Hexacode']['red_y'])
    green_x = int(config['Hexacode']['green_x'])
    green_y = int(config['Hexacode']['green_y'])
    blue_x = int(config['Hexacode']['blue_x'])
    blue_y = int(config['Hexacode']['blue_y'])

    
    # hexa code values in a specified range
    red_component = random.randint(red_x,red_y)
    green_component = random.randint(green_x,green_y)
    blue_component = random.randint(blue_x,blue_y)
    sparkles_random_colors = "#{:02X}{:02X}{:02X}".format(red_component,green_component,blue_component)
    sparkle.color(sparkles_random_colors)




    #sparkle.color(random.choice(sparkle_colors))
    sparkle.shapesize(random.uniform(shape_size_min,shape_size_max))
    sparkle.penup()
    sparkle.goto(random.randint(-500, 500),random.randint(-500, 500))
    return sparkle

# Function to move the object randomly
def move_randomly(obj):
    obj.setheading(random.randint(0, 360))
    obj.forward(random.randint(0, 100))

# Function to run the animation
def run_animation(max_frames):
    turtle.colormode(255)
    turtle.screensize(1920,1080)
    turtle.begin_fill()
    turtle.fillcolor(bgcolor)
    turtle.penup()
    turtle.goto(screen.window_width() / 2, screen.window_height() / 2)
    turtle.pendown()
    turtle.right(90)
    turtle.forward(screen.window_height())      
    turtle.right(90)
    turtle.forward(screen.window_width())      
    turtle.right(90)
    turtle.forward(screen.window_height())      
    turtle.right(90)
    turtle.forward(screen.window_width())      
    
    turtle.end_fill()

    sparkles = [create_sparkle() for _ in range(num_sparkles)]
    text_content = fetch_text_content()
    draw_text_content(text_content)
    
    frame_number = 0

    os.makedirs(output_images_folder, exist_ok=True)

    if os.path.exists(output_images_folder):
        shutil.rmtree(output_images_folder)
    
    os.makedirs(output_images_folder, exist_ok=True)

    # Clear existing video file
    if os.path.exists(output_video_file):
        os.remove(output_video_file)
    # Create the VideoWriter with specified resolution and fps
    fps = int(config['Animation']['fps'])
    video = cv2.VideoWriter(output_video_file, cv2.VideoWriter_fourcc(*'mp4v'), fps ,(resolution_x,resolution_y))

    while frame_number < max_frames:
        screen.update()

      
             
        # Move sparkles
        for sparkle in sparkles:
            move_randomly(sparkle)

        # Create new sparkles
        if random.random() < 15:
            sparkles.append(create_sparkle())

        # Save the current frame as an image
        filename = f"{output_images_folder}/frame_{frame_number:03d}.png"

        # Draw the background color manually
        #screen.bgcolor("black")
        screen.update()

        turtle.getcanvas().postscript(file=filename, colormode='color')
        img = Image.open(filename)
        img.save(filename)


        # Read the saved image and resize
        frame = cv2.imread(filename)
        frame = cv2.resize(frame, (resolution_x,resolution_y))
        

        # Capture frame for video
        video.write(frame)

        # Increment frame number
        frame_number += 1

        time.sleep(frame_delay)

    # Release the video writer
    video.release()

    # Clear the screen
    for sparkle in sparkles:
        sparkle.hideturtle()

    screen.bye()
    print(f"Video saved to: {output_video_file}")
    print(f"Frames saved to: {output_images_folder}")


# Run the animation
run_animation(max_frames)
