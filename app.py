from flask import Flask, request, send_file
from flask_cors import CORS
from PIL import Image, ImageSequence
import io
import os
import subprocess

app = Flask(__name__)
CORS(app)

@app.route('/compress_gif', methods=['POST'])
def compress_gif():
    file = request.files['file']
    max_colors = int(request.form.get('max_colors', 128))
    optimize = request.form.get('optimize', 'true').lower() == 'true'
    quality = int(request.form.get('quality', 75))

    original_gif = Image.open(file)

    compressed_frames = []
    for frame in ImageSequence.Iterator(original_gif):
        rgba_frame = frame.convert('RGBA')
        quantized_frame = rgba_frame.quantize(colors=max_colors)
        
        # Preserve transparency
        if 'transparency' in frame.info:
            quantized_frame.info['transparency'] = frame.info['transparency']
        
        compressed_frames.append(quantized_frame)

    output = io.BytesIO()
    compressed_frames[0].save(
        output,
        format='GIF',
        save_all=True,
        append_images=compressed_frames[1:],
        optimize=optimize,
        loop=0
    )
    output.seek(0)

    return send_file(output, mimetype='image/gif')

@app.route('/compress_video', methods=['POST'])
def compress_video():
    file = request.files['file']
    scale_factor = float(request.form.get('scale_factor', 0.5))  # Adjust as needed
    target_bitrate = request.form.get('target_bitrate', '500k')  # Default target bitrate

    # Save the uploaded file to a temporary location
    video_path = 'uploaded_video.mp4'  # Adjust path as needed
    file.save(video_path)

    # Define the output path for the compressed video
    compressed_video_path = 'compressed_video.mp4'  # Adjust path as needed

    # Run FFmpeg to compress the video
    ffmpeg_command = [
        'ffmpeg',
        '-i', video_path,
        '-vf', f'scale=iw*{scale_factor}:ih*{scale_factor}',
        '-b:v', target_bitrate,
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '28',
        compressed_video_path
    ]
    
    subprocess.run(ffmpeg_command, check=True)

    # Read the compressed video file into a BytesIO object
    with open(compressed_video_path, 'rb') as f:
        output = io.BytesIO(f.read())

    output.seek(0)

    # Clean up: remove the temporary video files
    os.remove(video_path)
    os.remove(compressed_video_path)

    # Return the compressed video file
    return send_file(output, mimetype='video/mp4')

if __name__ == '__main__':
    app.run(debug=True)
# import os
# import subprocess

# def compress_videos(folder_path):
#     for filename in os.listdir(folder_path):
#         if filename.endswith('.mov') or filename.endswith('.mp4'):

#             input_path = os.path.join(folder_path, filename)
#             output_path = os.path.join(folder_path, f'compressed_{filename}' )

#             ffmpeg_cmd = f'ffmpeg -i {input_path} -c:v libx264 -c:a copy -crf 20 {output_path}'
#             subprocess.run(ffmpeg_cmd, shell=True)

# folder_path = 'C:/Users/sa/Downloads/HASSAN_LOVE_BACKUP/HASSAN_LOVE_BACKUP/tmp'
# compress_videos(folder_path)