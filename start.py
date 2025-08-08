import get_data, write_html, webbrowser, speed_chart, accelerator_chart, combo_chart, get_hex, pathlib, os, shutil, stat

vin, data, fMode, chartsOpt = get_hex.select_source()

def show_final_window(vin):
    web_result = str(os.getcwd()) + "\\reports\\" + vin + "\\" + vin + "_report.html"
    webbrowser.open_new_tab(web_result)

bin_flags_table = []
table_data = {}
last_speed = 0
last_accel = 0

# The first twenty entries are not in order and can't be displayed chronologically. They have to be saved and sorted
# based on the oldest buffer value
buffer_list = []
speed_values = []
accelerator_values = []

buff_cnt = 0

isExist = os.path.exists("reports")
if not isExist:
    os.makedirs("reports")
    os.chmod("reports", stat.S_IWRITE)

isExist = os.path.exists("reports/"+vin)
if not isExist:
    os.makedirs("reports/"+vin+"/html")
    os.makedirs("reports/"+vin+"/charts")
    os.chmod("reports/"+vin+"/html", stat.S_IWRITE)
    os.chmod("reports/"+vin+"/charts", stat.S_IWRITE)

shutil.copy("output/d.gif", "reports/"+vin+"/html/d.gif")
shutil.copy("output/s.gif", "reports/"+vin+"/html/s.gif")
shutil.copy("output/u.gif", "reports/"+vin+"/html/u.gif")
shutil.copy("output/semke.png", "reports/"+vin+"/html/semke.png")
shutil.copy("output/semkewindow.png", "reports/"+vin+"/html/semkewindow.png")

def conv_hex_dec(hex_value):
    decimal_value = int(hex_value, 16)
    return decimal_value
def conv_hex_bin(hex_value):
    binary_value = str(bin(int(hex_value, 16))[2:].zfill(len(hex_value) * 4))
    return binary_value
def buffer_bytes(buffer_entry):
    buffer_fix = buffer_list[int(buffer_entry):] + buffer_list[:int(buffer_entry)]
    buff_cnt = last_speed = last_accel = 0

    for databytes in buffer_fix:
        bin_flags = conv_hex_bin(databytes[:2])
        table_data["offroad"], table_data["mudsnow"], table_data["parkbrake"], table_data["trailer"], \
            table_data["abs_act"], table_data["abs_stat"], table_data["atc_warn"], table_data["abs_warn"] \
            = get_data.do_1byte(bin_flags,fMode)

        bin_flags = conv_hex_bin(databytes[2:4])
        table_data["trigger"], table_data["accel_pct"], table_data["brk_light"] = get_data.do_2byte(bin_flags, fMode)
        accelerator_values.append(bin_flags[3:])                    # STORE THE ACCELERATOR VALUE

        bin_flags = conv_hex_bin(databytes[4:6])
        table_data["speed"], table_data["hsa_inter"] = get_data.do_3byte(bin_flags, fMode)
        speed_values.append(bin_flags[2:])                          # STORE THE SPEED VALUE

        bin_flags = conv_hex_bin(databytes[6:8])
        table_data["flr_aud"], table_data["flr_inter"], table_data["flr_stat"], table_data["cruise_stat"] \
            = get_data.do_4byte(bin_flags, fMode)

        bin_flags = conv_hex_bin(databytes[8:10])
        table_data["steer_angle"], table_data["vcd_brake"] = get_data.do_5byte(bin_flags, fMode)

        bin_flags = conv_hex_bin(databytes[10:12])
        table_data["esp_inter"], table_data["esp_stat"], table_data["driver_brake"] = get_data.do_6byte(bin_flags, fMode)

        if buff_cnt == 0:
            speed_change = 's'
        elif last_speed > float(table_data["speed"]):
            speed_change = 'd'
        elif last_speed < float(table_data["speed"]):
            speed_change = 'u'
        elif last_speed == float(table_data["speed"]):
            speed_change = 's'

        if buff_cnt == 0:
            accel_change = 's'
        elif last_accel > float(table_data["accel_pct"]):
            accel_change = 'd'
        elif last_accel < float(table_data["accel_pct"]):
            accel_change = 'u'
        elif last_accel == float(table_data["accel_pct"]):
            accel_change = 's'

        last_speed = float(table_data["speed"])
        last_accel = float(table_data["accel_pct"])


        write_html.write_data(vin,ECU_type, table_data, buff_cnt, speed_change, accel_change,fMode)
        buff_cnt += 1

    buffer_list.clear()
    buffer_fix.clear()

    return(last_speed, last_accel)

# SYSTEM INFORMATION
# The ABS ECU-Type is a one-byte identifier stored at location 0x03,
if (data[6:8]) == "04":
    ECU_type = "EC-80 ESP/ESP+"
    events_stored = 5
    parms = 22
elif (data[6:8]) == "05":
    ECU_type = "EC-80 ABS"
    events_stored = 4
    parms = 13
else:
    ECU_type = "EC-80 ATC or EC-60 Adv/Sta/Pre"

BDR_version = str(int(data[14:16]))
Events_cnt  = str(conv_hex_dec((data[17:24])))

write_html.write_sys_header(vin,ECU_type,BDR_version,Events_cnt,fMode)
data = data[32:]                                                        # DONE WITH SYSTEM INFO - REMOVE THOSE CHARACTERS

for z in range(5):
    ### DETERMINE EVENT NUMBER AND FIRST ENTRY OF BUFFER ###
    event = get_data.conv_hex_dec(data[4:12])
    buffer_entry = conv_hex_dec(data[26:28])

    event_header_list = []
    header = data[:40]

    event_header_list.append(header[28:36])                                                             # EVENT LOCK
    event_header_list.append(header[2:4])                                                               # EVENT COMPLETE
    event_header_list.append(get_data.conv_hex_dec(header[4:12]))                                       # EVENT NUMBER
    event_header_list.append(str('{:,}'.format(get_data.conv_hex_dec(header[12:20])*3)))                # ENGINE MINUTES
    event_header_list.append(str('{:,}'.format(get_data.conv_hex_dec(header[12:20]) * 3 / 60)))         # ENGINE HOURS
    event_header_list.append(str('{:,}'.format(round(get_data.conv_hex_dec(header[20:26])/6000, 1))))   # POWERUP MINUTES
    event_header_list.append(str('{:,}'.format(round(get_data.conv_hex_dec(header[20:26])/6000/60,1)))) # POWERUP HOURS
    event_header_list.append(header[38:40])                                                             # TRIGGER TYPE
    event_header_list.append(get_data.conv_hex_dec(header[36:38]))                                      # FDA TABLE INDEX

    ###### EVENT HEADER ######
    write_html.write_evt_header(vin,event_header_list)

    data = data[40:].lstrip("F").lstrip("0")            # DONE WITH HEADER INFO - REMOVE CHARACTERS AND PADDING

    ###### DETAIL LOOP #######
    write_html.write_detail_header(vin,ECU_type)

    for x in range(40):
        if x == 20:
            last_speed, last_accel = buffer_bytes(buffer_entry)
        if x < 20:
            buffer_list.append(data[:12])
        else:
            #print((x * .5)," | ","*" * 25,data[:12],"*"*25)
            #print(data[:2],conv_hex_bin(data[:2]),"FIRST BYTE")
            ### FIRST BYTE BREAKDOWN ###
            # 0 ABS Off-Road Switch
            # 1 ATC Mud/Snow Switch
            # 2 Park Brake Dash Ind. Request
            # 3 Trailer ABS Status
            # 4 ABS Activity
            # 5 ABS Status
            # 6 ATC Warning Lamp Request
            # 7 ABS Warning Lamp Request
            bin_flags = conv_hex_bin(data[:2])
            table_data["offroad"], table_data["mudsnow"],table_data["parkbrake"],table_data["trailer"],      \
                table_data["abs_act"], table_data["abs_stat"], table_data["atc_warn"], table_data["abs_warn"]   \
                = get_data.do_1byte(bin_flags, fMode)

            #print(data[2:4],conv_hex_bin(data[2:4]),"SECOND BYTE")
            ### SECOND BYTE BREAKDOWN ###
            # 0-4 Accelerator Pedal Position Pct
            # 5-6 CCVS Brake Light Request
            # 7   Trigger
            bin_flags = conv_hex_bin(data[2:4])
            accelerator_values.append(bin_flags[3:])
            table_data["trigger"], table_data["accel_pct"], table_data["brk_light"] = get_data.do_2byte(bin_flags,fMode)

            #print(data[4:6],conv_hex_bin(data[4:6]),"THIRD BYTE")
            ### THIRD BYTE BREAKDOWN ###
            # 0-5 Vehicle Speed
            # 6   HSA Intervention
            bin_flags = conv_hex_bin(data[4:6])
            speed_values.append(bin_flags[2:])                                  # SAVE THE SPEED VALUES FOR CHART
            table_data["speed"], table_data["hsa_inter"] = get_data.do_3byte(bin_flags, fMode)

            if ECU_type == "EC-80 ESP/ESP+":
                ### FOURTH BYTE BREAKDOWN ###
                # 0-2 FLR AUDIBLE ALERT
                # 3   FLR INTERVENTION
                # 4-5 FLR STATUS
                # 6-7 CRUISE CONTROL ACTIVE STATUS
                bin_flags = conv_hex_bin(data[6:8])
                table_data["flr_aud"],table_data["flr_inter"],table_data["flr_stat"], table_data["cruise_stat"] \
                    = get_data.do_4byte(bin_flags, fMode)

                ### FIFTH BYTE BREAKDOWN ###
                # 0-6 STEERING ANGLE DEGREE
                # 7   VCD BRAKE LAMP REQ
                bin_flags = conv_hex_bin(data[8:10])
                table_data["steer_angle"],table_data["vcd_brake"] = get_data.do_5byte(bin_flags, fMode)

                ### SIXTH BYTE BREAKDOWN ###
                # 4   ESP STATUS
                # 5   ESP INTERVENTION
                # 6-7 DRIVER SERVICE BRAKE APPLICATION
                bin_flags = conv_hex_bin(data[10:12])
                table_data["esp_inter"],table_data["esp_stat"],table_data["driver_brake"] = get_data.do_6byte(bin_flags, fMode)

            if last_speed > float(table_data["speed"]):
                speed_change = 'd'
            elif last_speed < float(table_data["speed"]):
                speed_change = 'u'
            elif last_speed == float(table_data["speed"]):
                speed_change = 's'

            if last_accel > float(table_data["accel_pct"]):
                accel_change = 'd'
            elif last_accel < float(table_data["accel_pct"]):
                accel_change = 'u'
            elif last_accel == float(table_data["accel_pct"]):
                accel_change = 's'

            last_speed = float(table_data["speed"])
            last_accel = float(table_data["accel_pct"])

            write_html.write_data(vin, ECU_type, table_data, x, speed_change, accel_change, fMode)

        if ECU_type == "EC-80 ESP/ESP+":
            data = data[12:]
        else:
            data = data[6:]

    write_html.write_footer(vin,event,chartsOpt)

    new_dir = pathlib.Path('reports', vin)
    new_dir.mkdir(parents=True, exist_ok=True)

    if chartsOpt == 1:
        speed_chart.make_speed_graph(vin,speed_values,event)
        accelerator_chart.make_accelerator_graph(vin,accelerator_values,event)
        combo_chart.make_combo_graph(vin,speed_values, accelerator_values, event)
    speed_values.clear()
    accelerator_values.clear()

show_final_window(vin)