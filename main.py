"""People Counter."""
"""
 Copyright (c) 2018 Intel Corporation.
 Permission is hereby granted, free of charge, to any person obtaining
 a copy of this software and associated documentation files (the
 "Software"), to deal in the Software without restriction, including
 without limitation the rights to use, copy, modify, merge, publish,
 distribute, sublicense, and/or sell copies of the Software, and to
 permit person to whom the Software is furnished to do so, subject to
 the following conditions:
 The above copyright notice and this permission notice shall be
 included in all copies or substantial portions of the Software.
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
 LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
 WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


import os
import sys
import time
import socket
import json
import cv2

import logging as log
import paho.mqtt.client as mqtt

from argparse import ArgumentParser
from inference import Network

from termcolor import colored #Color the output

# MQTT server environment variables
HOSTNAME = socket.gethostname()
MQTT_KEEPALIVE_INTERVAL = 60


def build_argparser():
    """
    Parse command line arguments.

    :return: command line arguments
    """
    parser = ArgumentParser()
    parser.add_argument("-i", '--input', help=i_desc, required=True,
                        help="Input file(number if camera, or file path to a videofile)")
    parser.add_argument("-d", '--device', help=d_desc, default='CPU',
                        help="Specify the target device to infer on: "
                        "CPU, GPU, FPGA or MYRIAD is acceptable. Sample "
                        "will look for a suitable plugin for device "
                        "specified (CPU by default)"))
    parser.add_argument("-o", help=o_desc, default="", help="If given, it will save a videofile with the result of the detection.")
    parser.add_argument("-m", '--model', help=m_desc, default="Model/person-detection-retail-0013.xml")
    parser.add_argument("-pt",'--prob_threshold', help=p_desc, type=float, default=0.5,
                        help="Probability threshold for detections filtering(0.5 by default)")
    parser.add_argument("--ip", help=ip_desc, type=str, default= socket.gethostbyname(HOSTNAME))
    parser.add_argument("-l", "--cpu_extension", required=False, type=str,
                        default=None, help="MKLDNN (CPU)-targeted custom layers."
                         "Absolute path to a shared library with the"
                         "kernels impl.")
    parser.add_argument("--port", help=port_desc, type=int, default=3001)
    parser.add_argument("-n", help=n_desc, type=str, default="entry.json")
    parser.add_argument("-x", help=x_desc, type=str, default="exit.json")
    parser.add_argument("--debug", help=debug_desc, type=bool, default=False)
    parser.add_argument("--headless", help=headless_desc, type=bool, default=False)
    return parser


def connect_mqtt(args):
    ### TODO: Connect to the MQTT client ###
    try:
        client = mqtt.Client(transport="websockets")
        client.connect(args.ip, port=args.port, keepalive=MQTT_KEEPALIVE_INTERVAL)
    except:
        print(colored("Can\'t connect to MQTT Server, please start the next time the program Mosquitto with mosquitto -c websockets.conf", 'yellow'))
        print(colored("Please read the Readme for more information",'yellow'))
    return client


def infer_on_stream(args, client):
    """
    Initialize the inference network, stream video to network,
    and output stats and video.

    :param args: Command line arguments parsed by `build_argparser()`
    :param client: MQTT client
    :return: None
    """
    detections = []
    maximum_ratio_difference = 0.07
    maximum_frame_difference = 10 #10 frames
    ids = list(range(0,100))
    out = None
    if args.o:
        out = cv2.VideoWriter(args.o, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), frame_rate, (frame_width, frame_height))
    entry_people = 0
    exit_people = 0
    process = True
    help = False
    scale = 5
    ret,frame = cap.read()
    action = ""
    color_help = (251,36,11)
    color_warning = (102,255,255)
    color_informative = (25,255,255)
    total_fps = 0
    total_fps_measurements = 0
    frame_counter = 0
    fps = 0
    mqttActive = True
    cv2.namedWindow("Output Video")
    if args.debug:
        cv2.namedWindow("Original")
        cv2.namedWindow("Past detection")
    global entry_parameters, exit_parameters
    global noEntryBox, noExitBox
    # Initialise the class
    infer_network = Network()
    # Set Probability threshold for detections
    prob_threshold = args.prob_threshold

    ### TODO: Load the model through `infer_network` ###
    infer_network.load_model(arg.model, device=args.device, cpu_extension=args.cpu_extension)

    ### TODO: Handle the input stream ###
    cap = cv2.VideoCapture(args.i)
    ret,frame = cap.read()
    frame_width = frame.shape[1]
    frame_height = frame.shape[0]
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    if not ret:
        print(colored("No image found, please check the videofile!",'red'))
        return
    ### TODO: Loop until stream is over ###
    if args.headless:
        print(colored("The app is running in headless mode!",'magenta'))
        print(colored("Please press Control + C to terminate",'magenta'))
        print(colored("To define new entry and exit boxes please disable headless mode!",'magenta'))
    if (args.headless and noExitBox) or (args.headless and noEntryBox) :
        sys.exit('Please disable the headless mode and select manually the entry and/or exit bounding boxes! Exiting')
    start = time.time() #Start time to calculate FPS
    signal.signal(signal.SIGINT,signal_handling)

    while cap.isOpened():
        if terminate:
            print(colored("Finishing the cycle", 'green'))
            break
        number_of_people = 0
        frame_number = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        ### TODO: Read from the video capture ###
        if process and not noExitBox and not noEntryBox:
            ret,frame = cap.read()
            if not ret:
                break
            output_frame = frame.copy()
            ### TODO: Pre-process the image as needed ###
            nw_shape = infer_network.get_input_shape()
            pp_frame = cv2.resize(frame, (nw_shape[3],  nw_shape[2]))
            pp_frame = np.transpose(pp_frame, (2,0,1))
            pp_frame = np.reshape(pp_frame, (1,nw_shape[1],nw_shape[2],nw_shape[3]))
            ### TODO: Start asynchronous inference for specified request ###
            infer_network.async_inference(pp_frame)
            ### TODO: Wait for the result ###
            while infer_network.wait():
                print(infer_network.wait())
            output = infer_network.extract_output()
            if args.debug:
                print("--------------------------------")
                print("Frame number: " + str(frame_number))
                print("--------------------------------")
            draw_color = (0, 0, 0)
            new_detections = []
            index = 0
            if args.debug:
                for x in detections:
                    cv2.circle(past_frame, x['current_location']['chest'], int(x['current_location']['width']/2), x['color'], 1)
                    cv2.putText(past_frame, str(x['id']), (x['current_location']['corner'][0], int(x['current_location']['corner'][1] + x['current_location']['height']/2) ), cv2.FONT_HERSHEY_SIMPLEX ,1, x['color'], 2, cv2.LINE_AA)
            for i in output[0][0]:
                if float(i[2]) > args.p:
                    location = {'corner':(0,0),'height':0, 'width':0, 'area':0, 'chest':(0,0), 'frame': 0}
                    p1x = int(i[3]*frame_width)
                    p1y = int(i[4]*frame_height)
                    p2x = int(i[5]*frame_width)
                    p2y = int(i[6]*frame_height)
                    location['corner'] = (p1x, p1y)
                    location['height'] = abs(p2y - p1y)
                    location['width'] = abs(p2x - p1x)
                    location['chest'] = (int(p1x + (p2x-p1x)/2), int(p1y + (p2y-p1y)/2))
                    location['area'] = (p2x - p1x)*(p2y-p1y)
                    location['frame'] = frame_number
                    distancep2_chest = cv2.norm(location['corner'], location['chest'], normType=cv2.NORM_L2)
                    sort_detection = []
                    for x in detections:
                        calculated_distance = cv2.norm(x['current_location']['chest'], location['chest'], normType=cv2.NORM_L2)
                        speed_distance = cv2.norm((int(x['current_location']['chest'][0] + x['tendency'][0]),int(x['current_location']['chest'][1] + x['tendency'][1])), location['chest'], normType=cv2.NORM_L2)
                        calculated_area_ratio =  0#abs(1.0 - area/x['location'][len(x['location'])-1]['area'])
                        calculated_difference_frames = abs(location['frame'] - x['frame_number'])
                        future_frame_distance = cv2.norm((int(x['current_location']['chest'][0] + x['tendency'][0]*calculated_difference_frames),int(x['current_location']['chest'][1] + x['tendency'][1]*calculated_difference_frames)), location['chest'], normType=cv2.NORM_L2)

                        if calculated_difference_frames > 0:
                            ratio = (detections.index(x), calculated_distance, calculated_area_ratio, calculated_difference_frames, future_frame_distance, speed_distance)
                            sort_detection.append(ratio)
                    sort_detection_meaning = sorted(sort_detection, key=lambda sort_detection: sort_detection[1])
                    sort_detection_future = sorted(sort_detection, key=lambda sort_detection: sort_detection[4])
                    if args.debug:
                        for lines in sort_detection_meaning[0:1]:
                            id = lines[0]
                            if len(detections[id]['past_locations']) > 0:
                                cv2.line(past_frame, location['chest'], detections[id]['past_locations'][-1]['chest'], detections[id]['color'],2)
                    if len(sort_detection_future) > 0:
                        id = sort_detection_future[0][0]
                        df = sort_detection_future[0][3]
                        length_line = 10
                        future_point = (int(detections[id]['current_location']['chest'][0] + detections[id]['tendency'][0]*df),int(detections[id]['current_location']['chest'][1] + detections[id]['tendency'][1]*df))
                        if args.debug:
                            cv2.line(past_frame, (future_point[0] + length_line, future_point[1]),(future_point[0] - length_line, future_point[1]), detections[id]['color'],2)
                            cv2.line(past_frame, (future_point[0], future_point[1] + length_line),(future_point[0], future_point[1]- length_line), detections[id]['color'],2)
                    if args.debug:
                        for lines in sort_detection_future[0:1]:
                            id = lines[0]
                            if len(detections[id]['past_locations']) > 0:
                                cv2.line(past_frame, location['chest'], detections[id]['past_locations'][-1]['chest'], detections[id]['color'],2)

                    if len(sort_detection_meaning)>0 and sort_detection_meaning[0][1] <= distancep2_chest and sort_detection_meaning[0][3] < maximum_frame_difference and sort_detection_meaning[0][3] > 0:
                        index = sort_detection_meaning[0][0]
                        id = detections[index]['id']
                        if args.debug:
                            print("¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡")
                            print("Distance checking")
                            print("Detected ID: " + str(id))
                            print(sort_detection_meaning[0:1])
                        detections[index] = update_existing(detections[index], location)
                        draw_color = detections[index]['color']
                        number_of_people+=1
                    elif len(sort_detection_future)>0 and sort_detection_future[0][4] <= distancep2_chest and sort_detection_future[0][3] < maximum_frame_difference and sort_detection_future[0][3] > 0:
                        if args.debug:
                            print("<><><><><><><><><><><><><><><><>")
                            print("Future distance checking!")
                            print(sort_detection_future[0:1])
                            print("Detected ID: " + str(id))
                        index = sort_detection_future[0][0]
                        id = detections[index]['id']
                        detections[index] = update_existing(detections[index], location)
                        draw_color = detections[index]['color']
                        number_of_people+=1
                    else:
                        if args.debug:
                            print("%%%%%%%%%%%%%%%%%%%%%")
                            print("New person detected!")
                            print("Detected ID: " + str(id))

                        tracker = {'id':0, 'current_location':{}, 'past_locations': [] , 'frame_number':0, 'color':(255,255,255), 'tendency': (0,0), 'vector': (0,0)}
                        tracker['current_location'] = location
                        tracker['color'] =  (int(uniform(125, 255)), int(uniform(125, 255)), int(uniform(125, 255)))
                        tracker['frame_number'] =  frame_number
                        tracker['id'] =  ids[0]
                        ids.pop(0)
                        detections.append(tracker)
                        id = tracker['id']
                        index = len(detections) - 1
                        draw_color = tracker['color']
                        number_of_people+=1
                    cv2.circle(output_frame, location['chest'], 3, draw_color, -1)
                    cv2.rectangle(output_frame,(p1x,p1y), (p2x, p2y), draw_color, 3)
                    cv2.putText(output_frame, str(id), (p1x,p1y) , cv2.FONT_HERSHEY_SIMPLEX ,
                               1, draw_color, 2, cv2.LINE_AA)
                    if len(detections) > 0:
                        if len(detections[index]['past_locations']) > 0:
                            cv2.line(output_frame, (int(location['corner'][0] + location['width']/2), location['corner'][1]), \
                            (int((location['corner'][0] + location['width']/2 + scale*detections[index]['tendency'][0])),\
                            int((location['corner'][1] + scale*detections[index]['tendency'][1]))), \
                             detections[index]['color'],3)

            for x in detections:
                if abs(x['frame_number'] - frame_number) > maximum_frame_difference:
                    uvx = 0
                    if x['tendency'][0] > 0 or x['tendency'][0] < 0:
                        uvx = int(x['tendency'][0]/abs(x['tendency'][0]))
                    uvy = 0
                    if x['tendency'][1] > 0 or x['tendency'][1] < 0:
                        uvy = int(x['tendency'][1]/abs(x['tendency'][1]))
                    tuv = (uvx, uvy)
                    if args.debug:
                        print("//////Deleting detected person///////////////")
                        print("ID: " + str(x['id']))
                        print("******************************")
                        print("TUV: " + str(tuv))
                        print(x['tendency'])
                        print("******************************")

                    if x['current_location']['chest'][0] + x['tendency'][0] > entry_parameters['points'][0][0] and \
                    x['current_location']['chest'][0] + x['tendency'][0] < entry_parameters['points'][1][0] and \
                    x['current_location']['chest'][1] + x['tendency'][1] > entry_parameters['points'][0][1] and \
                    x['current_location']['chest'][1] + x['tendency'][1] < entry_parameters['points'][1][1]:
                        coincidence = False
                        for uv in entry_parameters['u_vectors']:
                            if uv[0] == tuv[0] and uv[1] == tuv[1] and len(x['past_locations']) > 3:
                                coincidence = True
                                break
                        if coincidence:
                            if args.debug:
                                print("#######Person exited via entry box!########## ")
                            entry_people+=1
                            if mqttActive:
                                client.publish("entry", payload=str(entry_people))
                        if args.debug:
                            print("Exit via entry box Coincidence: " + str(coincidence))
                    if x['current_location']['chest'][0] + x['tendency'][0] > exit_parameters['points'][0][0] and \
                    x['current_location']['chest'][0] + x['tendency'][0] < exit_parameters['points'][1][0] and \
                    x['current_location']['chest'][1] + x['tendency'][1] > exit_parameters['points'][0][1] and \
                    x['current_location']['chest'][1] + x['tendency'][1] < exit_parameters['points'][1][1]:
                        coincidence = False
                        for uv in exit_parameters['u_vectors']:
                            if uv[0] == tuv[0] and uv[1] == tuv[1] and len(x['past_locations']) > 3:
                                coincidence = True
                                break
                        if coincidence:
                            if args.debug:
                                print("#######Person exited via exit box!########## ")
                            exit_people+=1
                            if mqttActive:
                                client.publish("exit", payload=str(exit_people))
                        if args.debug:
                            print("Exit via exit box coincidence: " + str(coincidence))
                    ids.append(x['id'])
                    detections.remove(x)
            frame_counter+=1
            if(time.time() - start) >= 1:
                fps = frame_counter
                total_fps += fps
                total_fps_measurements+=1
                start = time.time()
                frame_counter = 0
            #Send data every 60 frames
            if frame_number%60:
                if mqttActive:
                    client.publish("people", payload=str(number_of_people))
        else:
            output_frame = frame.copy()
        if args.o:
            out.write(output_frame)

        cv2.putText(output_frame, 'Toggle H for help', (int(3*output_frame.shape[1]/7),int(4*output_frame.shape[0]/7) ) , cv2.FONT_HERSHEY_SIMPLEX,0.75, color_help, 2, cv2.LINE_AA)
        if help:
            cv2.putText(output_frame, "Press: ", (int(3*output_frame.shape[1]/7),int(4.25*output_frame.shape[0]/7) ) , cv2.FONT_HERSHEY_SIMPLEX,0.78, color_help, 2, cv2.LINE_AA)
            cv2.putText(output_frame, "x: To select the exit bounding box", (int(3*output_frame.shape[1]/7),int(4.50*output_frame.shape[0]/7) ) , cv2.FONT_HERSHEY_SIMPLEX,0.83, color_help, 2, cv2.LINE_AA)
            cv2.putText(output_frame, "n: To select the entry bounding box", (int(3*output_frame.shape[1]/7),int(4.75*output_frame.shape[0]/7) ) , cv2.FONT_HERSHEY_SIMPLEX,0.88, color_help, 2, cv2.LINE_AA)
            cv2.putText(output_frame, "Space bar: Toggle to start/stop processing", (int(3*output_frame.shape[1]/7),int(5*output_frame.shape[0]/7) ) , cv2.FONT_HERSHEY_SIMPLEX,0.88, color_help, 2, cv2.LINE_AA)
            cv2.putText(output_frame, "Esc: Exit", (int(3*output_frame.shape[1]/7),int(5.25*output_frame.shape[0]/7) ) , cv2.FONT_HERSHEY_SIMPLEX,0.88, color_help, 2, cv2.LINE_AA)
            cv2.putText(output_frame, "Enter: Accept the selection", (int(3*output_frame.shape[1]/7),int(5.5*output_frame.shape[0]/7) ) , cv2.FONT_HERSHEY_SIMPLEX,0.88, color_help, 2, cv2.LINE_AA)

        if not entry_parameters['first_point'] and not entry_parameters['last_point']:
            cv2.putText(output_frame, "Please press \"n\" and click over the image to select the first entry point", (0,int(1*output_frame.shape[0]/7) ) , cv2.FONT_HERSHEY_SIMPLEX,0.88, color_informative, 2, cv2.LINE_AA)
        elif entry_parameters['first_point'] and not entry_parameters['last_point']:
            cv2.putText(output_frame, "Click over the image to select the last entry point", (0,int(1.3*output_frame.shape[0]/7) ) , cv2.FONT_HERSHEY_SIMPLEX,0.88, color_informative, 2, cv2.LINE_AA)
        elif not entry_parameters['complete_vectors']:
            cv2.putText(output_frame, "Please click inside the Entry Bounding Box to configure the entry directions, when finish press Enter key", (0,int(1.6*output_frame.shape[0]/7) ) , cv2.FONT_HERSHEY_SIMPLEX,0.70, color_informative, 2, cv2.LINE_AA)
        if not exit_parameters['first_point'] and not exit_parameters['last_point']:
            cv2.putText(output_frame, "Please press \"x\" and click over the image to select the first exit point", (0,int(5*output_frame.shape[0]/7) ) , cv2.FONT_HERSHEY_SIMPLEX,0.88, color_warning, 2, cv2.LINE_AA)
        elif exit_parameters['first_point'] and not exit_parameters['last_point']:
            cv2.putText(output_frame, "Please click over the image to select the last exit point", (0,int(5.3*output_frame.shape[0]/7) ) , cv2.FONT_HERSHEY_SIMPLEX,0.88, color_warning, 2, cv2.LINE_AA)
        elif not exit_parameters['complete_vectors']:
            cv2.putText(output_frame, "Please click inside the Exit Bounding Box to configure the exit directions, when finish press Enter key", (0 ,int(5.6*output_frame.shape[0]/7) ) , cv2.FONT_HERSHEY_SIMPLEX,0.70, color_warning, 2, cv2.LINE_AA)

        if entry_parameters['first_point']:
            cv2.rectangle(output_frame, entry_parameters['points'][0], entry_parameters['points'][1], entry_color, 3)
            cv2.rectangle(output_frame,(int(-40 + entry_parameters['points'][0][0] + (entry_parameters['points'][1][0] - entry_parameters['points'][0][0])/2), entry_parameters['points'][0][1]), (int(40 + entry_parameters['points'][0][0] + (entry_parameters['points'][1][0] - entry_parameters['points'][0][0])/2), entry_parameters['points'][0][1] + 30), (0,0,0), -1)
            cv2.putText(output_frame, 'Entry: ' + str(entry_people), (int(entry_parameters['points'][0][0] + (entry_parameters['points'][1][0] - entry_parameters['points'][0][0])/2 - 30), entry_parameters['points'][0][1] + 20) , cv2.FONT_HERSHEY_SIMPLEX,0.5, entry_color, 2, cv2.LINE_AA)
        if exit_parameters['first_point']:
            cv2.rectangle(output_frame, exit_parameters['points'][0], exit_parameters['points'][1], exit_color, 3)
            cv2.rectangle(output_frame,(int(-40 + exit_parameters['points'][0][0] + (exit_parameters['points'][1][0] - exit_parameters['points'][0][0])/2), exit_parameters['points'][0][1]), (int(40 + exit_parameters['points'][0][0] + (exit_parameters['points'][1][0] - exit_parameters['points'][0][0])/2), exit_parameters['points'][0][1] + 30), (0,0,0), -1)
            cv2.putText(output_frame, 'Exit: ' + str(exit_people), (int(exit_parameters['points'][0][0] + (exit_parameters['points'][1][0] - exit_parameters['points'][0][0])/2 - 30), exit_parameters['points'][0][1] + 20) , cv2.FONT_HERSHEY_SIMPLEX,0.5, exit_color, 2, cv2.LINE_AA)
        if exit_parameters['first_point'] and exit_parameters['last_point']:
            cv2.circle(output_frame, exit_parameters['center'],3, exit_color, 1)
            for uv in exit_parameters['u_vectors']:
                cv2.line(output_frame, exit_parameters['center'],(int(exit_parameters['center'][0] + 5*scale*uv[0]), int(exit_parameters['center'][1] + 3*scale*uv[1])), exit_color, 2  )
        if entry_parameters['first_point'] and entry_parameters['last_point']:
            cv2.circle(output_frame, entry_parameters['center'],3, entry_color, 1)
            for uv in entry_parameters['u_vectors']:
                cv2.line(output_frame, entry_parameters['center'],(int(entry_parameters['center'][0] + 5*scale*uv[0]), int(entry_parameters['center'][1] + 3*scale*uv[1])), entry_color, 2  )
        if not args.headless:
            cv2.rectangle(output_frame,(0, 30),  (100, 0), (0,0,0), -1)
            cv2.putText(output_frame, 'People: ' + str(number_of_people), (0, 20) , cv2.FONT_HERSHEY_SIMPLEX,0.5, (44,245,131), 2, cv2.LINE_AA)
            cv2.rectangle(output_frame,(int(6*output_frame.shape[1]/7), 30), (int(output_frame.shape[1]), 0), (0,0,0), -1)
            cv2.putText(output_frame, 'Frame number: ' + str(frame_number), (int(6*output_frame.shape[1]/7), 20) , cv2.FONT_HERSHEY_SIMPLEX, 0.5, (44,235,131), 2, cv2.LINE_AA)
            cv2.rectangle(output_frame,(int(output_frame.shape[1]/2-30), output_frame.shape[0] - 40), (int(output_frame.shape[1]/2+40), output_frame.shape[0]), (0,0,0), -1)
            cv2.putText(output_frame, 'FPS: ' + str(fps), (int(output_frame.shape[1]/2  - 20), int(output_frame.shape[0] - 10)) , cv2.FONT_HERSHEY_SIMPLEX, 0.5, (44,235,131), 2, cv2.LINE_AA)

            cv2.imshow("Output Video", output_frame)
            if args.debug:
                cv2.imshow("Original", frame)
                cv2.imshow("Past detection", past_frame)
            k = cv2.waitKey(30)
            if k == 27:
                break
            elif k == 32: #Space
                process = not process
            elif k == 104: #h OR h
                help = not help
            elif k == 120: #x or X
                action = "exit"
                exit_parameters = {'points': [(0,0),(0,0)], 'center': (0,0), 'u_vectors':[], 'first_point': False, 'last_point': False, 'complete_vectors': False}
            elif k == 110: #n or N
                entry_parameters = {'points': [(0,0),(0,0)], 'center': (0,0), 'u_vectors':[], 'first_point': False, 'last_point': False, 'complete_vectors': False}
                action = "entry"
            elif k == 13 or k == 271: #Enter
                if action == "entry":
                    entry_parameters['complete_vectors'] = True
                    noEntryBox = False
                elif action == "exit":
                    exit_parameters['complete_vectors'] = True
                    noExitBox = False
                action = ""

    print(colored("=================People counted======================", 'green'))
    print(colored("Entry: " + str(entry_people), 'green'))
    print(colored("Exit: " + str(exit_people), 'green'))
    print(colored("=====================================================", 'green'))
    if total_fps_measurements > 0:
        print(colored("~~~~~~~~~~~~~~~~~~~~~~~~Performance~~~~~~~~~~~~~~~~~~~~~~~~", 'green'))
        print(colored("Average FPS: " + str(int(total_fps/total_fps_measurements)), 'green'))
        print(colored("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", 'green'))

    with open(args.n, 'w') as outfilen:
        json.dump(entry_parameters, outfilen)
    print(colored("Saved entry parameters as: " + args.n,'cyan'))
    with open(args.x, 'w') as outfilex:
        json.dump(exit_parameters, outfilex)
    print(colored("Saved exit parameters as: " + args.x,'cyan'))
    cv2.destroyAllWindows()
    cap.release()
    client.disconnect()
    if args.o:
        out.release()

            ### TODO: Get the results of the inference request ###

            ### TODO: Extract any desired stats from the results ###

            ### TODO: Calculate and send relevant information on ###
            ### current_count, total_count and duration to the MQTT server ###
            ### Topic "person": keys of "count" and "total" ###
            ### Topic "person/duration": key of "duration" ###

        ### TODO: Send the frame to the FFMPEG server ###

        ### TODO: Write an output image if `single_image_mode` ###


def main():
    """
    Load the network and parse the output.

    :return: None
    """
    # Grab command line args
    args = build_argparser().parse_args()
    # Connect to the MQTT server
    client = connect_mqtt(args)
    # Perform inference on the input stream
    infer_on_stream(args, client)


if __name__ == '__main__':
    main()