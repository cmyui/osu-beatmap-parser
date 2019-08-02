import os
import time
from datetime import datetime
start_full_time = time.time()

global RED, GREEN, CYAN, PINK, YELLOW, ENDC
RED    = '\033[91m'
ENDC   = '\033[0m'
GREEN  = '\033[92m'
CYAN   = '\033[96m'
PINK   = '\033[95m'
YELLOW = '\033[93m'

global debug
debug = True

global NEWL
NEWL = "\r\n" if os.name == "nt" else "\n"

try: # Open up a pipe for osu beatmap.
    global f
    f = open("beatmap.osu", "r")
except: handle_error("Beatmap file could not be found.", 1)


def osu_pixels(cs):
    """
    Calculate "osu!pixels" from our circle size.
    """

    return 54.4 - 4.48 * cs


def handle_error(err, exit, type=0):
    """
    Handle errors a nice and elegant way.
    
    :String err: Our error.
    :Boolean exit: Whether to halt the program because of this error.
    :Integer type: The type of log. 0: Error, 1: Warning.
    """

    log_file = open("parser.log", "a+")
    print(f"{YELLOW if type else RED}{err}{ENDC}")
    log_file.write(f"[{'WARN' if type else 'ERROR'}] [{datetime.now().strftime('%Y-%m-%d %I:%M:%S:%f%p')}] {err}{NEWL}")
    log_file.close()
    del log_file
    if exit: os._exit(exit)


# Our main function.
def ParseBeatmap(f):
    """
    Parse the full beatmap given.
    This will return all variables in locals().

    **I'm not sure if this is unorthodox, but in my case, I think it will work best this way for what I want it to do.**

    That means this function is a mess of a memory map!

    Return will include all information from every section of the beatmap.
    """

    _data = f.read()

    # Check if beatmap is empty.
    if not _data: handle_error(f"{RED}Beatmap file is either empty, or failed to be read.{ENDC}", 1)

    data = _data.split(NEWL)
    del _data

    # Now that we have our data cached, close our pipe.
    f.close()
    del f

    # Check for fucked formatting?
    # Do this to find broken things right off the bat.
    try: osu_file_version = int(data[0][-2:].replace("v", ""))
    except: handle_error(f"{RED}Beatmap file is invalid, and could not be parsed.{ENDC}", 1)

    print(f"{CYAN}osu file format: v{osu_file_version}{ENDC}")

    if osu_file_version < 14: handle_error("At the moment, this parser only supports osu! file verions >= 14.", 1)

    _SECTIONS = []

    for line in data:
        if not line: continue # ignore empty lines
        if line[0] == "[" and line[-1] == "]": _SECTIONS.append(f"----{line[1:-1].lower()}") # Delimiter = "--" for
        else: _SECTIONS.append(line)
    del data

    SECTIONS = NEWL.join(_SECTIONS).split("----")
    del _SECTIONS

    for _section in SECTIONS:
        key, val = [None] * 2
        section = _section.split("\n")
        del _section

        if section[0] == "general": # [General]
            AudioFilename, AudioFilename, PreviewTime, Countdown, SampleSet, StackLeniency, Mode, LetterboxInBreaks, WidescreenStoryboard = [None] * 9
            for line in section[1:]:
                if not line: continue # TODO: this above instead of on every one?
                key, val = line.split(": ")

                if key == "AudioFilename": AudioFilename = str(val)
                elif key == "AudioLeadIn": AudioLeadIn = int(val)
                elif key == "PreviewTime": PreviewTime = int(val)
                elif key == "Countdown": Countdown = int(val)
                elif key == "SampleSet": SampleSet = str(val)
                elif key == "StackLeniency": StackLeniency = float(val)
                elif key == "Mode": Mode = bool(val)
                elif key == "LetterboxInBreaks": LetterboxInBreaks = bool(val)
                elif key == "WidescreenStoryboard": WidescreenStoryboard = bool(val)
                elif key == "SpecialStyle": SpecialStyle = bool(val)
                elif key == "UseSkinSprites": UseSkinSprites = bool(val)
                else: handle_error(f"Unknown key \"{key}\" in section - general.", 0, 1)
            del key, val # Theres no way it's faster to have it in the loop, right? lol im too stoned to b coding

            # Actual TODO: this is stupid? why even bother? this will fuck up previous .osu versions. Stop doing shit like this!
            ## TODO: this in every section.
            #if not all([AudioFilename, AudioFilename, PreviewTime, Countdown, SampleSet, StackLeniency, Mode, LetterboxInBreaks, WidescreenStoryboard]):
            #    handle_error(f"{RED}A required variable was not found in the [General] section.{ENDC}", 1)

        # I don't know why anyone would ever care about this?
        # TODO?: Perhaps add a flag to disable for speed improvements for "normal" users.
        elif section[0] == "editor": # [Editor]
            for line in section[1:]:
                if not line: continue
                key, val = line.split(": ")

                if key == "Bookmarks": Bookmarks = val.split(",")
                elif key == "DistanceSpacing": DistanceSpacing = float(val)
                elif key == "BeatDivisor": BeatDivisor = int(val)
                elif key == "GridSize": GridSize = int(val)
                elif key == "TimelineZoom": TimelineZoom = float(val)
                else: handle_error(f"Unknown key \"{key}\" in section - editor.", 0, 1)
            del key, val

        elif section[0] == "metadata": # [Metadata]
            for line in section[1:]:
                if not line: continue
                key, val = line.split(":")

                if key == "Title": Title = str(val)
                elif key == "TitleUnicode": TitleUnicode = str(val)
                elif key == "Artist": Artist = str(val)
                elif key == "ArtistUnicode": ArtistUnicode = str(val)
                elif key == "Creator": Creator = str(val)
                elif key == "Version": Version = str(val)
                elif key == "Source": Source = str(val)
                elif key == "Tags": Tags = str(val)
                elif key == "BeatmapID": BeatmapID = int(val)
                elif key == "BeatmapSetID": BeatmapSetID = int(val)
                else: handle_error(f"Unknown key \"{key}\" in section - metadata.", 0, 1)
            del key, val

        elif section[0] == "difficulty": # [Difficulty]
            for line in section[1:]:
                if not line: continue
                key, val = line.split(":")

                if key == "HPDrainRate": HPDrainRate = float(val)
                elif key == "CircleSize":
                    CircleSize = float(val)
                    OsuPixels  = osu_pixels(CircleSize)
                elif key == "OverallDifficulty": OverallDifficulty = float(val)
                elif key == "ApproachRate": ApproachRate = float(val)
                elif key == "SliderMultiplier": SliderMultiplier = float(val)
                elif key == "SliderTickRate": SliderTickRate = float(val)
                else: handle_error(f"Unknown key \"{key}\" in section - difficulty.", 0, 1)
            del key, val

        elif section[0] == "events": # [Events]
            Breaks = []
            Videos = []
            for line in section[1:]:
                if not line or line[0:1] == "//": continue
                val = line.split(",")

                if val[0] == '0':
                    BackgroundFileName = val[2]
                elif val[0] == '2':
                    Breaks.append(f"{val[1]}:{val[2]}") # Append start to end.
                elif val[0] == 'Video':
                    Videos.append([val[1], val[2]]) # StartTime, filename (w/ extension)
                # TODO Storyboards, bg colours, videos, etc.
                del val

        elif section[0] == "timingpoints": # [TimingPoints]
            TimingPoints = []
            for line in section[1:]:
                if not line: continue

                _copy        = line.split(",")
                offset       = int(_copy[0])
                ms_per_beat  = float(_copy[1])
                meter        = int(_copy[2])
                sample_set   = int(_copy[3])
                sample_index = int(_copy[4])
                volume       = int(_copy[5])
                inherited    = bool(_copy[6])
                kiai_mode    = bool(_copy[7])
                del _copy

                TimingPoints.append({"Offset": offset, "MSPerBeat": ms_per_beat, "Meter": meter,
                                    "SampleSet": sample_set, "Volume": volume,
                                    "Inherited": inherited,"KiaiMode": kiai_mode})
                del offset, ms_per_beat,  \
                    meter, sample_set,    \
                    sample_index, volume, \
                    inherited, kiai_mode

        elif section[0] == "colours": # [Colours]
            Colours = []
            for line in section[1:]:
                if not line: continue
                key, val = line.split(" : ")

                Colours.append({key: val})
            del key, val

        elif section[0] == "hitobjects": # [HitObjects]
            HitObjects = [] # TODO: ACTUALLY unpack "extras" everywhere! .split(":")!@!@!@@ TODO: actually just make a function?
            for line in section[1:]:
                if not line: continue
                split = line.split(",")
                split_len = len(split)
                x, y, object_time, object_type, hitSound = split[:5] # standard for every object type

                if int(object_type) & 1: # Hitcircle
                    circle_start_time = time.time()

                    # TODO: fail hitcircle stuff
                    #handle_error(f"FAILED HITCIRCLE - {split}", 0)

                    if split_len == 6:
                        extras = split[5]
                        HitObjects.append({"x": x, "y": y, "time": object_time, "type": object_type, "hitSound": hitSound, "extras": extras})
                        del extras
                    else: HitObjects.append({"x": x, "y": y, "time": object_time, "type": object_type, "hitSound": hitSound})

                    if debug: print(f"{PINK}READ HITCIRCLE{ENDC} Time taken: {'%.3f' % round((time.time() - circle_start_time) * 1000000, 3)} microseconds.")
                    del circle_start_time

                elif int(object_type) & 2: # Slider
                    slider_start_time = time.time()
                    if split_len not in (8, 11):
                        del slider_start_time
                        handle_error(f"FAILED SLIDER - {split}", 0)
                        continue

                    # Split up sliderType and curvePoints by |.
                    _s = split[5].split("|")
                    sliderType, curvePoints = _s[0], _s[1:]

                    # Grab vital slider information.
                    repeat, pixelLength = split[6:8]

                    # Check for optionals if they have been included.
                    # Append to HitObjects array.
                    if split_len > 8:
                        edgeHitsounds, edgeAdditions, extras = split[8:]
                        HitObjects.append({"x": x, "y": y, "time": object_time, "type": object_type, "hitSound": hitSound, "sliderType": sliderType, "curvePoints": curvePoints, "repeat": repeat, "pixelLength": pixelLength, "edgeHitsounds": edgeHitsounds, "edgeAdditions": edgeAdditions, "extras": extras})
                        del edgeHitsounds, edgeAdditions, extras
                    else: HitObjects.append({"x": x, "y": y, "time": object_time, "type": object_type, "hitSound": hitSound, "sliderType": sliderType, "curvePoints": curvePoints, "repeat": repeat, "pixelLength": pixelLength})

                    del _s, sliderType, curvePoints, repeat, pixelLength

                    if debug: print(f"{GREEN}READ SLIDER{ENDC} Time taken: {'%.3f' % round((time.time() - slider_start_time) * 1000000, 3)} microseconds.")
                    del slider_start_time

                elif int(object_type) & 8: # Spinner
                    spinner_start_time = time.time()
                    if split_len != 7:
                        del spinner_start_time
                        handle_error(f"FAILED SPINNER - {split}", 0)
                        continue

                    endTime = split[5]
                    if split_len == 7:
                        extras = split[6]
                        HitObjects.append({"x": x, "y": y, "time": object_time, "type": object_type, "hitSound": hitSound, "endTime": endTime, "extras": extras})
                        del extras
                    else: HitObjects.append({"x": x, "y": y, "time": object_time, "type": object_type, "hitSound": hitSound, "endTime": endTime})

                    del endTime
                    if debug: print(f"{YELLOW}READ SPINNER{ENDC} Time taken: {'%.3f' % round((time.time() - spinner_start_time) * 1000000, 3)} microseconds.")
                    del spinner_start_time


                del split, x, y, object_time, object_type, hitSound, split_len

        del section, line, key, val

    del SECTIONS

    # Just return literally everything we've done.
    # Since we memory handle properly, it returns only the relevant data.
    return locals()


if __name__ == "__main__":
    BeatmapData = ParseBeatmap(f)

    print(BeatmapData)
    print(f"\n{CYAN}DONE. Time taken: {'%.3f' % round((time.time() - start_full_time) * 1000, 1)} milliseconds.{ENDC}")

del start_full_time,    \
    RED, GREEN, CYAN,   \
    PINK, YELLOW, ENDC, \
    NEWL, debug
    #^^^^^^^^^^^^^^^^^^^^ why? TODO: check if this is faster there is literally no way it doesnot just do this automaitcally but i need to know how it works now that i've thought about it im gonna learn the whole ass thing