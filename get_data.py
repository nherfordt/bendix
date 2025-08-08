def conv_hex_dec(hex_value):
    decimal_value = int(hex_value, 16)
    return decimal_value


def conv_hex_dec(hex_value):
    decimal_value = int(hex_value, 16)
    return decimal_value


def conv_bin_dec(bin_value):
    dec_value = int(bin_value, 2)
    return dec_value


def reverse_the_bits(bitstring):
    bitstring = bitstring.lstrip('0')[::-1]
    return bitstring


def binary_to_decimal_negative(binary):
    if binary[0] == '1':
        inverted_binary = ''.join(['1' if bit == '0' else '0' for bit in binary])
        decimal_value = int(inverted_binary, 2) + 1
        return -decimal_value
    else:
        return int(binary, 2)

def do_1byte(bin_flags, fMode):
    if fMode == 1:
        offroad = mudsnow = parkbrake = trailer = abs_act = abs_stat = atc_warn = abs_warn = "OFF"

        if bin_flags[:1] == "1":
            abs_warn = "ON"
        if bin_flags[1:2] == "1":
            atc_warn = "ON"
        if bin_flags[2:3] == "1":
            abs_stat = "ON"
        if bin_flags[3:4] == "1":
            abs_act = "ON"
        if bin_flags[4:5] == "1":
            trailer = "ON"
        if bin_flags[5:6] == "1":
            parkbrake = "ON"
        if bin_flags[6:7] == "1":
            mudsnow = "ON"
        if bin_flags[7:8] == "1":
            offroad = "ON"
    else:
        abs_warn = bin_flags[:1]
        atc_warn = bin_flags[1:2]
        abs_stat = bin_flags[2:3]
        abs_act = bin_flags[3:4]
        trailer = bin_flags[4:5]
        parkbrake = bin_flags[5:6]
        mudsnow = bin_flags[6:7]
        offroad = bin_flags[7:8]

    return (offroad, mudsnow, parkbrake, trailer, abs_act, abs_stat, atc_warn, abs_warn)

def do_1byte60(bin_flags, fMode):
    eventIDmaster = conv_bin_dec(bin_flags[:2])

    if fMode == 1:
        abs_act = abs_stat = atc_warn = abs_warn = "OFF"

        if bin_flags[4:5] == "1":
            abs_act = "ON"
        if bin_flags[5:6] == "1":
            abs_stat = "ON"
        if bin_flags[6:7] == "1":
            atc_warn = "ON"
        if bin_flags[7:8] == "1":
            abs_warn = "ON"
    else:
        abs_act = bin_flags[4:5]
        abs_stat = bin_flags[5:6]
        atc_warn = bin_flags[6:7]
        abs_warn = bin_flags[7:8]

    return (eventIDmaster, abs_act, abs_stat, atc_warn, abs_warn)

def do_2byte(bin_flags, fMode):
    if fMode == 1:
        if bin_flags[:1] == "1":  # TRIGGER INDICATOR
            trigger = "ON"
        else:
            trigger = "OFF"
    else: trigger = bin_flags[:1]

    accelerator_pos_pct = conv_bin_dec(bin_flags[3:])
    accelerator_pos_pct = format(accelerator_pos_pct * 3.2, '.1f')

    if fMode == 1:
        if str(bin_flags[1:3]) == "00":  # BRAKE LIGHT REQUEST
            brk_light_req = "OFF"  # 0 BINARY
        elif str(bin_flags[1:3]) == "01":  # 1 BINARY
            brk_light_req = "ON"
        elif str(bin_flags[1:3]) == "10":  # 2 BINARY
            brk_light_req = "UNK"
        else:
            brk_light_req = "RESERVED"
    else: brk_light_req = str(conv_bin_dec(bin_flags[1:3]))

    return (trigger, accelerator_pos_pct, brk_light_req)

def do_3byte(bin_flags, fMode):
    veh_speed = conv_bin_dec(bin_flags[2:])
    veh_speed = format(veh_speed / .44704, '.2f')

    if fMode == 1:
        if bin_flags[1:2] == "1":  # HSA INTERVENTION
            hsa_inter = "ON"
        else:
            hsa_inter = "OFF"
    else: hsa_inter = bin_flags[1:2]

    return (veh_speed, hsa_inter)

def do_4byte(bin_flags, fMode):
    flr_aud = int(conv_bin_dec(bin_flags[5:]))  # AUDIBLE ALERT WARNING

    if fMode == 1:
        if bin_flags[4:5] == "0":  # FLR INTERVENTION
            flr_inter = "ON"       # 3 FLR INTERVENTION
        else:
            flr_inter = "OFF"

        if bin_flags[2:4] == "00":  # FLR STATUS
            flr_stat = "Abnormal"  # 4-5 FLR STATUS
        elif bin_flags[2:4] == "01":
            flr_stat = "Normal"
        elif bin_flags[2:4] == "10" or "11":
            flr_stat = "Unk"
        else:
            flr_stat = "?????"

        if bin_flags[:2] == "00":  # CRUISE CONTROL ACTIVE STATUS
            cruise_stat = "OFF"  # 6-7 CRUISE CONTROL ACTIVE STATUS
        elif bin_flags[:2] == "01":
            cruise_stat = "ON"
        elif bin_flags[:2] == "10":
            cruise_stat = "Error"
        elif bin_flags[:2] == "11":
            cruise_stat = "Not Available"
        else:
            cruise_stat = "!! FAILURE !!"
    else:
        if bin_flags[4:5] == "1":
            flr_inter = "0"
        else: flr_inter = "1"
        flr_stat = conv_bin_dec(bin_flags[2:4])
        cruise_stat = conv_bin_dec(bin_flags[:2])

    return (flr_aud, flr_inter, flr_stat, cruise_stat)

def do_5byte(bin_flags, fMode):
    steering_binary = bin_flags[1:]
    steer_angle = binary_to_decimal_negative(steering_binary)

    steer_angle = format(steer_angle * 5.37203, '.2f')

    if fMode == 1:
        if bin_flags[:1] == "1":
            vcd_brake = "ON"
        else:
            vcd_brake = "OFF"
    else: vcd_brake = bin_flags[:1]

    return (steer_angle, vcd_brake)

def do_5byte60(bin_flags, fMode):
    eventIDslave = conv_bin_dec(bin_flags[:2])

    if fMode == 1:
        offroad = mudsnow = parkbreak = trailer = "OFF"
        if bin_flags[4:5] == "1":
            offroad = "ON"
        if bin_flags[5:6] == "1":
            mudsnow = "ON"
        if bin_flags[6:7] == "1":
            parkbreak = "ON"
        if bin_flags[7:8] == "1":
            trailer = "ON"
    else:
        offroad = bin_flags[4:5]
        mudsnow = bin_flags[5:6]
        parkbreak = bin_flags[6:7]
        trailer = bin_flags[7:8]

    return (eventIDslave, offroad, mudsnow, parkbreak, trailer)

def do_6byte(bin_flags, fMode):
    driver_brake = conv_bin_dec(bin_flags[:2])  # DRIVER BREAK

    if fMode == 1:
        esp_inter = esp_stat = "OFF"
        if bin_flags[2:3] == "1":  # ESP INTERVENTION
            esp_inter = "ON"
        if bin_flags[3:4] == "1":  # ESP STATUS
            esp_stat = "ON"
    else:
        esp_inter = bin_flags[2:3]
        esp_stat = bin_flags[3:4]

    return (esp_inter, esp_stat, driver_brake)

def do_6byte60(bin_flags, fMode):
    trigger_slave = ""
    veh_speed = conv_bin_dec(bin_flags[0:5])

    veh_speed = format(veh_speed / .44704, '.2f')

    hsa_inter = bin_flags[6:7]   # HSA INTERVENTION
    if fMode:
        if hsa_inter == "1":
            hsa_inter = "ON"
        else: hsa_inter = "OFF"

    if bin_flags[7:8] == "1":
        trigger_slave = "ON"

    return (veh_speed, hsa_inter, trigger_slave)