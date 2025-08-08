import os, pathlib, shutil
import get_data, write_html, speed_chart, accelerator_chart, combo_chart

REPO_ROOT = os.path.dirname(__file__)

def conv_hex_dec(hex_value): 
    return int(hex_value, 16) if hex_value else 0

def conv_hex_bin(hex_value): 
    return str(bin(int(hex_value, 16))[2:].zfill(len(hex_value) * 4)) if hex_value else "0"* (len(hex_value)*4)

def _mkdirs_safe(*dirs):
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        try: os.chmod(d, 0o755)
        except PermissionError: pass

def generate_report(vin, data, fMode, chartsOpt, output_root):
    os.chdir(output_root)

    table_data = {}
    speed_values, accelerator_values, buffer_list = [], [], []
    last_speed = 0.0
    last_accel = 0.0

    reports_root = os.path.join(output_root, "reports")
    vin_root     = os.path.join(reports_root, vin)
    html_dir     = os.path.join(vin_root, "html")
    charts_dir   = os.path.join(vin_root, "charts")
    _mkdirs_safe(reports_root, vin_root, html_dir, charts_dir)

    # Copy static assets
    for name in ["d.gif", "s.gif", "u.gif", "semke.png", "semkewindow.png"]:
        for folder in ["static", "assets"]:
            src = os.path.join(REPO_ROOT, folder, name)
            if os.path.exists(src):
                shutil.copy(src, os.path.join(html_dir, name))
                break

    def buffer_bytes(buffer_entry, ECU_type, last_speed_local, last_accel_local):
        nonlocal buffer_list, speed_values, accelerator_values, table_data
        buff_cnt = 0
        buffer_fix = buffer_list[int(buffer_entry):] + buffer_list[:int(buffer_entry)]

        for databytes in buffer_fix:
            bin_flags = conv_hex_bin(databytes[:2])
            (table_data["offroad"], table_data["mudsnow"], table_data["parkbrake"], table_data["trailer"],
             table_data["abs_act"], table_data["abs_stat"], table_data["atc_warn"], table_data["abs_warn"]) =                 get_data.do_1byte(bin_flags, fMode)

            bin_flags = conv_hex_bin(databytes[2:4])
            table_data["trigger"], table_data["accel_pct"], table_data["brk_light"] = get_data.do_2byte(bin_flags, fMode)
            accelerator_values.append(bin_flags[3:])

            bin_flags = conv_hex_bin(databytes[4:6])
            table_data["speed"], table_data["hsa_inter"] = get_data.do_3byte(bin_flags, fMode)
            speed_values.append(bin_flags[2:])

            if len(databytes) >= 8:
                bin_flags = conv_hex_bin(databytes[6:8])
                out4 = get_data.do_4byte(bin_flags, fMode)
                if isinstance(out4, (tuple, list)) and len(out4) == 4:
                    (table_data["flr_aud"], table_data["flr_inter"], table_data["flr_stat"], table_data["cruise_stat"]) = out4
            if len(databytes) >= 10:
                bin_flags = conv_hex_bin(databytes[8:10])
                out5 = get_data.do_5byte(bin_flags, fMode)
                if isinstance(out5, (tuple, list)) and len(out5) == 2:
                    (table_data["steer_angle"], table_data["vcd_brake"]) = out5
            if len(databytes) >= 12:
                bin_flags = conv_hex_bin(databytes[10:12])
                out6 = get_data.do_6byte(bin_flags, fMode)
                if isinstance(out6, (tuple, list)) and len(out6) == 3:
                    (table_data["esp_inter"], table_data["esp_stat"], table_data["driver_brake"]) = out6

            speed_change = 's' if buff_cnt == 0 else ('d' if last_speed_local > float(table_data.get("speed", 0) or 0) else ('u' if last_speed_local < float(table_data.get("speed", 0) or 0) else 's'))
            accel_change = 's' if buff_cnt == 0 else ('d' if last_accel_local > float(table_data.get("accel_pct", 0) or 0) else ('u' if last_accel_local < float(table_data.get("accel_pct", 0) or 0) else 's'))

            last_speed_local = float(table_data.get("speed", 0) or 0)
            last_accel_local = float(table_data.get("accel_pct", 0) or 0)

            write_html.write_data(vin, ECU_type, table_data, buff_cnt, speed_change, accel_change, fMode)
            buff_cnt += 1

        buffer_list.clear()
        buffer_fix.clear()
        return last_speed_local, last_accel_local

    if len(data) >= 8 and (data[6:8]) == "04":
        ECU_type = "EC-80 ESP/ESP+"
    elif len(data) >= 8 and (data[6:8]) == "05":
        ECU_type = "EC-80 ABS"
    else:
        ECU_type = "EC-80 ATC or EC-60 Adv/Sta/Pre"

    BDR_version = str(int(data[14:16],16)) if len(data) >= 16 else "0"
    Events_cnt  = str(conv_hex_dec(data[17:24])) if len(data) >= 24 else "0"

    write_html.write_sys_header(vin, ECU_type, BDR_version, Events_cnt, fMode)
    data = data[32:] if len(data) > 32 else ""

    for z in range(5):
        if len(data) < 40:
            break
        event = int(data[4:12], 16) if len(data) >= 12 else 0
        buffer_entry = conv_hex_dec(data[26:28]) if len(data) >= 28 else 0

        event_header_list = []
        header = data[:40]

        event_header_list.append(header[28:36] if len(header) >= 36 else "")
        event_header_list.append(header[2:4] if len(header) >= 4 else "")
        event_header_list.append(int(header[4:12],16) if len(header) >= 12 else 0)
        event_header_list.append(str('{:,}'.format(int(header[12:20],16)*3)) if len(header) >= 20 else "0")
        event_header_list.append(str('{:,}'.format(int(header[12:20],16)*3/60)) if len(header) >= 20 else "0")
        event_header_list.append(str('{:,}'.format(round(int(header[20:26],16)/6000,1))) if len(header) >= 26 else "0")
        event_header_list.append(str('{:,}'.format(round(int(header[20:26],16)/6000/60,1))) if len(header) >= 26 else "0")
        event_header_list.append(header[38:40] if len(header) >= 40 else "")
        event_header_list.append(int(header[36:38],16) if len(header) >= 38 else 0)

        write_html.write_evt_header(vin, event_header_list)
        data = data[40:].lstrip("F").lstrip("0")

        write_html.write_detail_header(vin, ECU_type)

        x = 0
        while x < 40 and len(data) >= (12 if ECU_type == "EC-80 ESP/ESP+" else 6):
            if x == 20:
                last_speed, last_accel = buffer_bytes(buffer_entry, ECU_type, last_speed, last_accel)
            if x < 20:
                buffer_list.append(data[:12])
            else:
                bin_flags = conv_hex_bin(data[:2])
                (table_data["offroad"], table_data["mudsnow"], table_data["parkbrake"], table_data["trailer"],
                 table_data["abs_act"], table_data["abs_stat"], table_data["atc_warn"], table_data["abs_warn"]) =                     get_data.do_1byte(bin_flags, fMode)

                bin_flags = conv_hex_bin(data[2:4])
                accelerator_values.append(bin_flags[3:])
                (table_data["trigger"], table_data["accel_pct"], table_data["brk_light"]) = get_data.do_2byte(bin_flags, fMode)

                bin_flags = conv_hex_bin(data[4:6])
                speed_values.append(bin_flags[2:])
                (table_data["speed"], table_data["hsa_inter"]) = get_data.do_3byte(bin_flags, fMode)

                if ECU_type == "EC-80 ESP/ESP+":
                    bin_flags = conv_hex_bin(data[6:8]); out4 = get_data.do_4byte(bin_flags, fMode)
                    (table_data["flr_aud"], table_data["flr_inter"], table_data["flr_stat"], table_data["cruise_stat"]) = out4
                    bin_flags = conv_hex_bin(data[8:10]); out5 = get_data.do_5byte(bin_flags, fMode)
                    (table_data["steer_angle"], table_data["vcd_brake"]) = out5
                    bin_flags = conv_hex_bin(data[10:12]); out6 = get_data.do_6byte(bin_flags, fMode)
                    (table_data["esp_inter"], table_data["esp_stat"], table_data["driver_brake"]) = out6

                speed_change = 'd' if last_speed > float(table_data["speed"]) else ('u' if last_speed < float(table_data["speed"]) else 's')
                accel_change = 'd' if last_accel > float(table_data["accel_pct"]) else ('u' if last_accel < float(table_data["accel_pct"]) else 's')

                last_speed = float(table_data["speed"])
                last_accel = float(table_data["accel_pct"])

                write_html.write_data(vin, ECU_type, table_data, x, speed_change, accel_change, fMode)

            if ECU_type == "EC-80 ESP/ESP+":
                data = data[12:]
            else:
                data = data[6:]
            x += 1

        write_html.write_footer(vin, event, chartsOpt)

        pathlib.Path(vin_root).mkdir(parents=True, exist_ok=True)
        if chartsOpt == 1:
            speed_chart.make_speed_graph(vin, speed_values, event)
            accelerator_chart.make_accelerator_graph(vin, accelerator_values, event)
            combo_chart.make_combo_graph(vin, speed_values, accelerator_values, event)
        speed_values.clear()
        accelerator_values.clear()

    final_path = os.path.join(vin_root, f"{vin}_report.html")
    with open(final_path, "rb") as f:
        return f.read()
