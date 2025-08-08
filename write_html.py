import get_data
def write_sys_header(vin,ECU_type,BDR_version,Events_cnt,fMode):
    file = open("reports/"+vin+"/"+vin+"_report.html", "w")

    html_header_start = """
        <html>
        <head>
        <meta name="viewport" content="initial-scale=1.0, user-scalable=no" />
        <meta http-equiv="content-type" content="text/html; charset=UTF-8"/>
        <style type="text/css">
        body, td, th, p {
          font-family: Verdana, Arial, Helvetica, sans-serif;
          font-size: 12px;
          text-align: center; 
          vertical-align: middle;
        }
    """
    html_header_css = """
        .bgON {
         background-color: #98e0c1;
         text-align: center; 
         vertical-align: middle;
        }
        .bgOFF {
         background-color: #e09191;
         text-align: center; 
         vertical-align: middle;
        }
        .bgUnk {
         background-color: #c8c8c8;
         text-align: center; 
         vertical-align: middle;
        }
        .bgRESERVED {
         background-color: #e5e5e5;
         text-align: center; 
         vertical-align: middle;
        }
        tr:hover td {
        background-color: #00616b;
        color: white;
        }
        .bgYellow {
         background-color: #feffb4;
         text-align: center; 
         vertical-align: middle;
        }
        .bgGold {
         background-color: #f5d489;
         text-align: center; 
         vertical-align: middle;
        }    
        """
    html_header_end = """
        @media print {
        .pagebreak {
        clear: both;
        min-height: 1px;
        page-break-after: always;
        }}
        </style>
        <link rel='icon' href='https://semke.com/wp-content/uploads/files/2016/cropped-favicon-32x32.png' sizes='32x32'/>
        <link rel='icon' href='https://semke.com/wp-content/uploads/files/2016/cropped-favicon-192x192.png' sizes='192x192'/>
        <link rel='apple-touch-icon' href='https://semke.com/wp-content/uploads/files/2016/cropped-favicon-180x180.png'/>
        <title>SEMKE FORENSIC | Discover the Truth</title>
        </head>
        </body><table width='100%' cellpadding='0' cellspacing='0'><tr bgcolor="white"><td align='left'>
        <img src='html/semke.png'></td><td align='left'>
    """
    if fMode == 1:
        html_header = html_header_start + html_header_css + html_header_end
    else:
        html_header = html_header_start + html_header_end

    file.write(html_header)
    file.write("<h1>ECU Type: "+ECU_type+"</h1>\n")
    file.write("<h1>BDR Version: "+BDR_version+"</h1>\n")
    file.write("<h1>Events: "+Events_cnt+"</h1></td></tr></table>\n")
    file.close()

def write_footer(vin, event,charts):
    file = open("reports/"+vin+"/"+vin+"_report.html", "a")
    html_footer = """
    </table>\n<br>
    <hr><br>
    """
    html_charts = """
    <table width='100%' cellpadding='0' cellspacing='0'>\n<tr bgcolor='white'>\n
    <td width=33% align='center'><img src='charts/VIN-speed_EVENT.png' width='500' height='412'></td>\n
    <td width=33% align='center'><img src='charts/VIN-combo_EVENT.png' width='500' height='412'></td>\n
    <td width=33% align='center'><img src='charts/VIN-accelerator_EVENT.png' width='500' height='412'></td>\n
    </tr></table><br><br><br>
    """
    if charts == 1:
        html_footer = html_footer + html_charts
        html_footer = html_footer.replace("EVENT",str(event))
        html_footer = html_footer.replace("VIN",str(vin))
    file.write(html_footer)
    file.close()
def write_evt_header(vin,data):
    print(data)
    if str(data[1]) == "55":  # 55 = Event Complete
        Evt_complete = "YES"
    else:
        Evt_complete = "NO"

    # An Event Lock Number equal to 0xFFFF indicates an event that is “Not Locked” and subject to being overwritten.
    if data[0] == "FFFFFFFF":
            Evt_lock_num = "Not locked"
    else:
        Evt_lock_num = str(data[2])

    if data[7] == "01":                                                                             #
       data[7] = "> 0.5 g"
    elif data[7] == "02":
       data[7] = "Driver Override - Collision Mitigation System"
    elif data[7] == "04":
       data[7] = "Hard Brake"
    elif data[7] == "08":
        data[7] = "Automatic Emergency Braking<br>(AEB)"
    else:
        data[7] = "Unk"

    file = open("reports/"+vin+"/"+vin+"_report.html", "a")

    file.write("<div class='pagebreak'></div>")

    if data[2] == 4294967295:
        file.write("\n<h2>**** NO DATA FOR THIS EVENT ****</h2>\n")

    file.write("\n<h2>Event Complete: " + Evt_complete + " | ")
    file.write("\nEvent Lock Number: " + Evt_lock_num + "</h2>\n")

    html_event_header = """
    <table width='100%' border='1' cellpadding='0' cellspacing='0'><tr><td><table width='90%' align='center'><tr>\
    <th><font size='3'>Event Num</font></th><th><font size='3'>Engine Mins</font></th><th><font size='3'>\
    Engine Hrs</font></th><th><font size='2'>Powerup Mins</font></th><th><font size='3'>Powerup Hrs</font>\
    </th><th><font size='3'>Trigger Type</font></th><th><font size='3'>FDA Table Index</font></th></tr>
    """

    file.write(html_event_header)
    file.write("<tr>")
    for x in range(7):
        file.write("<td align='center'><font size='3'>" + str(data[x+2]) + "</font></td>")
    file.write("</tr></table></td></tr></table>")

    file.close()

def write_detail_header(vin,ECU_type):
    file = open("reports/"+vin+"/"+vin+"_report.html", "a")

    ESP_ESP_header = """
       <br><table width='100%' cellspacing='0' cellpadding='2' border='1' class='hoverTable'><tr bgcolor='#d8d8d5'>\
       <th width='4%'>Time</th><th width='4%'>Trigger</th><th width='4%'>FLR Status</th><th width='4%'>ABS Status</th>\
       <th width='4%'>Trailer ABS Status</th><th width='4%'>ESP Status</th><th width='4%'>ABS Warning Lamp Request</th>\
       <th width='4%'>ATC Warning Lamp Request</th><th width='4%'>ATC Mud/Snow Switch</th><th width='4%'>ABS Off-Road \
       Switch</th><th width='6%'>Vehicle Speed (mph)</th><th width='6%'>Steering Angle</th><th width='6%'>Accelerator\
       <br>Pedal<br>Position (%)</th><th width='4%'>CCVS Brake Light Request</th><th width='5%'>Driver Service Brake<br>\
       Application<sup>#</sup></th><th width='4%'>Park Brake Dash Ind. Request</th><th width='4%'>Cruise Control Active Status</th>\
       <th width='4%'>VCD Brake Lamp Request</th><th width='5%'>FLR Audible Alert</th><th width='4%'>FLR Intervention\
       </th><th width='4%'>ABS Activity</th><th width='4%'>ESP Intervention</th><th width='4%'>HSA Intervention</th>\
       """
    EC80_ATC_header = """
       <br><table width='100%' cellspacing='0' cellpadding='2' border='1' class='hoverTable'><tr bgcolor='#d8d8d5'>\
       <th width='4%'>Time</th><th width='4%'>Trigger</th><th width='4%'>ABS Status</th><th width='4%'>Trailer ABS Status</th>\
       <th width='4%'>ABS Warning Lamp Request</th><th width='4%'>ATC Warning Lamp Request</th><th width='4%'>\
       ATC Mud/Snow Switch</th><th width='4%'>ABS Off-Road Switch</th><th width='6%'>Vehicle Speed (mph)</th>\
       <th width='6%'>Accelerator<br>Pedal<br>Position (%)</th><th width='4%'>CCVS Brake Light Request</th>\
       <th width='4%'>Park Brake Dash Ind. Request</th><th width='4%'>ABS Activity</th><th width='4%'>HSA Intervention</th>\
       """
    EC60_Adv_header = """
       <br><table width='100%' cellspacing='0' cellpadding='2' border='1' class='hoverTable'><tr bgcolor='#d8d8d5'>\
       <th width='4%'>Time</th><th width='4%'>Trigger</th><th width='4%'>FLR Status</th><th width='4%'>ABS Status</th>\
       <th width='4%'>Trailer ABS Status</th><th width='4%'>ESP Status</th><th width='4%'>ABS Warning Lamp Request</th>\
       <th width='4%'>ATC Warning Lamp Request</th><th width='4%'>ATC Mud/Snow Switch</th><th width='4%'>ABS Off-Road \
       Switch</th><th width='6%'>Vehicle Speed (mph)</th><th width='6%'>Steering Angle</th><th width='6%'>Accelerator\
       <br>Pedal<br>Position (%)</th><th width='4%'>CCVS Brake Light Request</th><th width='5%'>Driver Service Brake<br>\
       Application<sup>#</sup></th><th width='4%'>Park Brake Dash Ind. Request</th><th width='4%'>Cruise Control Active Status</th>\
       <th width='4%'>VCD Brake Lamp Request</th><th width='5%'>FLR Audible Alert</th><th width='4%'>FLR Intervention\
       </th><th width='4%'>ABS Activity</th><th width='4%'>ESP Intervention</th><th width='4%'>HSA Intervention</th>\
       """

    if ECU_type == "EC-80 ESP/ESP+":
        header = ESP_ESP_header
    elif ECU_type == "EC-80 ATC or EC-60 Adv/Sta/Pre":
        header = EC80_ATC_header
    elif ECU_type == "EC-60 Adv":
        header = EC60_Adv_header

    file.write(header)
    file.close()

def write_data(vin,ECU_type,table_data, time_cnt, last_speed, last_accel,fMode):
    file = open("reports/"+vin+"/"+vin+"_report.html", "a")

    file.write("<tr><td class='bgYellow'>" + str(time_cnt * .5) + "</td>\n")
    file.write("<td class='bg" + table_data["trigger"] + "'>" + table_data["trigger"] + "</td>\n")
    if ECU_type == "EC-80 ESP/ESP+":
        file.write("<td class='bgGold'>" + str(table_data["flr_stat"]) + "</td>\n")
    file.write("<td class='bg" + table_data["abs_stat"] + "'>" + table_data["abs_stat"] + "</td>\n")
    file.write("<td class='bg" + table_data["trailer"] + "'>" + table_data["trailer"] + "</td>\n")
    if ECU_type == "EC-80 ESP/ESP+":
        file.write("<td class='bg" + table_data["esp_stat"] + "'>" + table_data["esp_stat"] + "</td>\n")
    file.write("<td class='bg" + table_data["abs_warn"] + "'>" + table_data["abs_warn"] + "</td>\n")
    file.write("<td class='bg" + table_data["atc_warn"] + "'>" + table_data["atc_warn"] + "</td>\n")
    file.write("<td class='bg" + table_data["mudsnow"] + "'>" + table_data["mudsnow"] + "</td>\n")
    file.write("<td class='bg" + table_data["offroad"] + "'>" + table_data["offroad"] + "</td>\n")

    if table_data["speed"] != "":
        if fMode == 1:
            file.write(
                "<td align='center'>" + str(table_data["speed"]) + "<img src='html/" + last_speed + ".gif'></td>\n")
        else:
            file.write("<td align='center'>" + str(table_data["speed"]) + "</td>\n")
    else:
        file.write("<td> </td>\n")

    if ECU_type == "EC-80 ESP/ESP+":
        if table_data["steer_angle"] != "":
            if fMode == 1:
                file.write("<td align='center'>"+ str(table_data["steer_angle"]) + "&deg;</td>\n")
            else: file.write("<td align='center'>"+ str(table_data["steer_angle"]) + "</td>\n")
        else:
            file.write("<td></td>\n")

    if table_data["accel_pct"] != "0":
        if fMode == 1:
            file.write("<td align='center'>" + str(table_data["accel_pct"]) + "<img src='html/" + str(
                last_accel) + ".gif'</td>\n")
        else:
            file.write("<td align='center'>" + str(table_data["accel_pct"]) + "</td>\n")
    else:
        file.write("<td></td>\n")

    file.write("<td class='bg" + table_data["brk_light"] + "'>" + table_data["brk_light"] + "</td>\n")

    driver_brake = bgcolor = ""
    if ECU_type == "EC-80 ESP/ESP+":
        if fMode == 1:
            if table_data["driver_brake"] == 0:
                driver_brake = "0&nbsp;<&nbsp;1/2"
                bgcolor = "#A8DADC"
            elif table_data["driver_brake"] == 1:
                driver_brake = "1/2&nbsp;-&nbsp;2"
                bgcolor = "#457B9D"
            elif table_data["driver_brake"] == 2:
                driver_brake = "2-6"
                bgcolor = "#E76F51"
            elif table_data["driver_brake"] == 3:
                driver_brake = ">&nbsp;6"
                bgcolor = "#D62828"
        else:
            bgcolor = "#FFFFFF"
            driver_brake = int(table_data["driver_brake"])
        file.write("<td align='center' bgcolor='" + bgcolor + "'>" + str(driver_brake) + "</td>\n")

    file.write("<td class='bg" + table_data["parkbrake"] + "'>" + str(table_data["parkbrake"]) + "</td>\n")

    if ECU_type == "EC-80 ESP/ESP+":
        file.write("<td class='bg" + str(table_data["cruise_stat"]) + "' align='center'>" + str(table_data["cruise_stat"]) + "</td>\n")
        file.write("<td class='bg" + table_data["vcd_brake"] + "'>" + table_data["vcd_brake"] + "</td>\n")

        if fMode == 1:
            if table_data["flr_aud"] == 0:                                                          # 0-2 FLR AUDIBLE ALERT
                flr_aud = "No Warning"
                bgcolor = "#D3D3D3"
            elif table_data["flr_aud"] == 1:
                flr_aud = "Distance Alert 1"
                bgcolor = "#A8E6CF"
            elif table_data["flr_aud"] == 2:
                flr_aud = "Distance Alert 2"
                bgcolor = "#FFD166"
            elif table_data["flr_aud"] == 3:
                flr_aud = "Distance Alert 3"
                bgcolor = "#FF8C42"
            elif table_data["flr_aud"] == 4:
                flr_aud = "System Shutdown Alert"
                bgcolor = "#D7263D"
            elif table_data["flr_aud"] == 5:
                flr_aud = "Impact Alert"
                bgcolor = "#800020"
            elif table_data["flr_aud"] == 6:
                flr_aud = "Error"
                bgcolor = "#6C5B7B"
            elif table_data["flr_aud"] == 7:
                flr_aud = "Not Available"
                bgcolor = "#808080"
            else:
                flr_aud = "?????"
                bgcolor = "#FFFFFF"
        else:
            flr_aud = table_data["flr_aud"]
            bgcolor = "#FFFFFF"

        if table_data["flr_aud"] > 3:
            if fMode == 1:
                file.write("<td align='center' bgcolor='" + bgcolor + "'><font color='white'>" + str(flr_aud) + "</font></td>\n")
            else:
                file.write("<td align='center'>" + str(flr_aud) + "</td>\n")
        else:
            file.write("<td align='center' bgcolor='" + bgcolor + "'>" + str(flr_aud) + "</td>\n")

        file.write("<td class='bg" + table_data["flr_inter"] + "'>" + table_data["flr_inter"] + "</td>\n")

    file.write("<td class='bg" + table_data["abs_act"] + "'>" + table_data["abs_act"] + "</td>\n")

    if ECU_type == "EC-80 ESP/ESP+":
        file.write("<td class='bg" + table_data["esp_inter"] + "'>" + table_data["esp_inter"] + "</td>\n")
    file.write("<td class='bg" + table_data["hsa_inter"] + "'>" + table_data["hsa_inter"] + "</td>\n")

    file.close()

def write_data60(time_cnt, vin, ECU_type,table_data, last_speed, last_accel, fMode):
    bgcolor = driver_brake = ""

    file = open("reports/"+vin+"/"+vin+"_report.html", "a")

    file.write("<tr><td class='bgYellow'>" + str(time_cnt * .5) + "</td>\n")
    file.write("<td class='bg" + table_data["trigger"] + "'>" + table_data["trigger"] + "</td>\n")

    if ECU_type == "EC-80 ESP/ESP+" or ECU_type == "EC-60 Adv":
        file.write("<td class='bgGold'>" + str(table_data["flr_stat"]) + "</td>\n")

    file.write("<td class='bg" + table_data["abs_stat"] + "'>" + table_data["abs_stat"] + "</td>\n")
    file.write("<td class='bg" + table_data["trailer"] + "'>" + table_data["trailer"] + "</td>\n")
    if ECU_type == "EC-80 ESP/ESP+" or ECU_type == "EC-60 Adv":
        file.write("<td class='bg" + table_data["esp_stat"] + "'>" + table_data["esp_stat"] + "</td>\n")
    file.write("<td class='bg" + table_data["abs_warn"] + "'>" + table_data["abs_warn"] + "</td>\n")
    file.write("<td class='bg" + table_data["atc_warn"] + "'>" + table_data["atc_warn"] + "</td>\n")
    file.write("<td class='bg" + table_data["mudsnow"] + "'>" + table_data["mudsnow"] + "</td>\n")
    file.write("<td class='bg" + table_data["offroad"] + "'>" + table_data["offroad"] + "</td>\n")

    if table_data["accel_pct"] != "0":
        if fMode == 1:
            file.write("<td align='center'>" + str(table_data["accel_pct"]) + "<img src='html/" + str(
                last_accel) + ".gif'</td>\n")
        else:
            file.write("<td align='center'>" + str(table_data["accel_pct"]) + "</td>\n")
    else:
        file.write("<td></td>\n")

    if table_data["steer_angle"] != "":
        if fMode == 1:
            file.write("<td align='center'>" + str(table_data["steer_angle"]) + "&deg;</td>\n")
        else:
            file.write("<td align='center'>" + str(table_data["steer_angle"]) + "</td>\n")
    else:
        file.write("<td></td>\n")

    if table_data["accel_pct"] != "0":
        if fMode == 1:
            file.write("<td align='center'>" + str(table_data["accel_pct"]) + "<img src='html/" + str(
                last_accel) + ".gif'</td>\n")
        else:
            file.write("<td align='center'>" + str(table_data["accel_pct"]) + "</td>\n")
    else:
        file.write("<td></td>\n")

    file.write("<td class='bg" + table_data["brk_light"] + "'>" + table_data["brk_light"] + "</td>\n")

    if fMode == 1:
        if table_data["driver_brake"] == 0:
            driver_brake = "0&nbsp;<&nbsp;1/2"
            bgcolor = "#A8DADC"
        elif table_data["driver_brake"] == 1:
            driver_brake = "1/2&nbsp;-&nbsp;2"
            bgcolor = "#457B9D"
        elif table_data["driver_brake"] == 2:
            driver_brake = "2-6"
            bgcolor = "#E76F51"
        elif table_data["driver_brake"] == 3:
            driver_brake = ">&nbsp;6"
            bgcolor = "#D62828"
    else:
        bgcolor = "#FFFFFF"
        driver_brake = int(table_data["driver_brake"])
    file.write("<td align='center' bgcolor='" + bgcolor + "'>" + str(driver_brake) + "</td>\n")

    file.write("<td class='bg" + table_data["parkbrake"] + "'>" + table_data["parkbrake"] + "</td>\n")

    if ECU_type == "EC-80 ESP/ESP+" or ECU_type == "EC-60 Adv":
        file.write("<td class='bg" + str(table_data["cruise_stat"]) + "' align='center'>" + str(table_data["cruise_stat"])
                   + "</td>\n")
        file.write("<td class='bg" + table_data["vcd_brake"] + "'>" + table_data["vcd_brake"] + "</td>\n")

        if fMode == 1:
            if table_data["flr_aud"] == 0:  # 0-2 FLR AUDIBLE ALERT
                flr_aud = "No Warning"
                bgcolor = "#D3D3D3"
            elif table_data["flr_aud"] == 1:
                flr_aud = "Distance Alert 1"
                bgcolor = "#A8E6CF"
            elif table_data["flr_aud"] == 2:
                flr_aud = "Distance Alert 2"
                bgcolor = "#FFD166"
            elif table_data["flr_aud"] == 3:
                flr_aud = "Distance Alert 3"
                bgcolor = "#FF8C42"
            elif table_data["flr_aud"] == 4:
                flr_aud = "System Shutdown Alert"
                bgcolor = "#D7263D"
            elif table_data["flr_aud"] == 5:
                flr_aud = "Impact Alert"
                bgcolor = "#800020"
            elif table_data["flr_aud"] == 6:
                flr_aud = "Error"
                bgcolor = "#6C5B7B"
            elif table_data["flr_aud"] == 7:
                flr_aud = "Not Available"
                bgcolor = "#808080"
            else:
                flr_aud = "?????"
                bgcolor = "#FFFFFF"
        else:
            flr_aud = table_data["flr_aud"]
            bgcolor = "#FFFFFF"

        if table_data["flr_aud"] > 3:
            if fMode == 1:
                file.write("<td align='center' bgcolor='" + bgcolor + "'><font color='white'>" + str(
                    flr_aud) + "</font></td>\n")
            else:
                file.write("<td align='center'>" + str(flr_aud) + "</td>\n")
        else:
            file.write("<td align='center' bgcolor='" + bgcolor + "'>" + str(flr_aud) + "</td>\n")

        file.write("<td class='bg" + table_data["flr_inter"] + "'>" + table_data["flr_inter"] + "</td>\n")

    file.write("<td class='bg" + table_data["abs_act"] + "'>" + table_data["abs_act"] + "</td>\n")

    file.write("<td class='bg" + table_data["esp_inter"] + "'>" + table_data["esp_inter"] + "</td>\n")
    file.write("<td class='bg" + table_data["hsa_inter"] + "'>" + table_data["hsa_inter"] + "</td>\n")

    file.close()