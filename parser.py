import os
import time
from datetime import datetime


""" Define some global variables we'll be using throughout the program. """

global GREEN, CYAN, PINK, YELLOW, RED, ENDC, NEWL, debug
GREEN  = '\033[92m'
CYAN   = '\033[96m'
PINK   = '\033[95m'
YELLOW = '\033[93m'
RED    = '\033[91m'
ENDC   = '\033[0m'
NEWL   = "\r\n" if os.name == "nt" else "\n"
debug = False


""" Now for our functions. """

def osu_pixels(cs):
    """
    Calculate "osu!pixels" from our circle size.
    """

    return 54.4 - 4.48 * cs


def ParseBeatmap(fileText, file=None, IncludeEditor=False):
    """
    Parse the full beatmap given.
    This will return all variables in locals().

    **I'm not sure if this is unorthodox, but in my case, I think it will work best this way for what I want it to do.**

    That means this function is a mess of a memory map!

    Return will include all information from every section of the beatmap.
    """

    if file: # Check if the user sent a file object, or is just sending raw text.
        # Read data from beatmap, splitting it by newlines.
        data = file.read().splitlines()
        if not data: return "Beatmap file is either empty, or failed to be read."
        file.close()
        del file
    else: # User sent raw text.
        data = fileText.splitlines()
        if not data: return "Data is either empty, or failed to be read."
        del fileText

    # Check for fucked formatting?
    # Do this to find broken things right off the bat.
    try: osu_file_version = int(data[0][-2:].replace("v", ""))
    except: return "Beatmap file is invalid, and could not be parsed."

    print(f"{CYAN}osu file format: v{osu_file_version}{ENDC}")

    if osu_file_version < 14: return "At the moment, this parser only supports osu! file verions >= 14."

    _SECTIONS = []

    for line in data[2:]:
        if not line: continue # ignore empty lines
        if line[0] == "[" and line[-1] == "]":
            _SECTIONS.append(f"----{line[1:-1].lower()}") # Delimiter
        else: _SECTIONS.append(line)
    del data, line

    SECTIONS = NEWL.join(_SECTIONS).split("----")

    del _SECTIONS

    # yikes
    AudioFilename, AudioLeadIn, PreviewTime, Countdown, SampleSet, StackLeniency, Mode, LetterboxInBreaks, WidescreenStoryboard, SpecialStyle, UseSkinSprites, \
    Bookmarks, DistanceSpacing, BeatDivisor, GridSize, TimelineZoom, \
    Title, TitleUnicode, Artist, ArtistUnicode, Creator, Version, Source, Tags, BeatmapID,BeatmapSetID, \
    HPDrainRate, CircleSize, OverallDifficulty, ApproachRate, SliderMultiplier, SliderTickRate, \
    BackgroundFileName, Breaks, Videos, \
    TimingPoints, \
    Colours, \
    HitObjects = [None] * 38

    for _section in SECTIONS:
        section = _section[:-1].split("\n")
        del _section

        if section[0] == "general": # [General]

            for line in section[1:]:
                if ": " in line: key, val = line.split(": ")
                else: print(f"{YELLOW}[WARN] Unknown line format \"{line}\" in [General] section.{ENDC}");continue
                try:
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
                    else: print(f"{YELLOW}[WARN] Unknown key \"{key}\" in [General] section.{ENDC}")
                    del key, val
                except: return ".osu file format is invalid."
            del line

        elif section[0] == "editor" and IncludeEditor: # [Editor]
            for line in section[1:]:
                if ": " in line: key, val = line.split(": ")
                else: print(f"{YELLOW}[WARN] Unknown line format \"{line}\" in [Editor] section.{ENDC}");continue

                try:
                    if key == "Bookmarks": Bookmarks = val.split(",")
                    elif key == "DistanceSpacing": DistanceSpacing = float(val)
                    elif key == "BeatDivisor": BeatDivisor = int(val)
                    elif key == "GridSize": GridSize = int(val)
                    elif key == "TimelineZoom": TimelineZoom = float(val)
                    else: print(f"{YELLOW}[WARN] Unknown key \"{key}\" in [Editor] section.{ENDC}")
                    del key, val
                except: return ".osu file format is invalid."
            del line

        elif section[0] == "metadata": # [Metadata]
            for line in section[1:]:
                if ":" in line: key, val = line.split(":")
                else: print(f"{YELLOW}[WARN] Unknown line format \"{line}\" in [Metadata] section.{ENDC}");continue

                try:
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
                    else: print(f"{YELLOW}[WARN] Unknown key \"{key}\" in [Metadata] section.{ENDC}")
                    del key, val
                except: return ".osu file format is invalid."
            del line

        elif section[0] == "difficulty": # [Difficulty]
            for line in section[1:]:
                if ":" in line: key, val = line.split(":")
                else: print(f"{YELLOW}[WARN] Unknown line format \"{line}\" in [Difficulty] section.{ENDC}");continue

                try:
                    if key == "HPDrainRate": HPDrainRate = float(val)
                    elif key == "CircleSize": CircleSize = float(val)
                    elif key == "OverallDifficulty": OverallDifficulty = float(val)
                    elif key == "ApproachRate": ApproachRate = float(val)
                    elif key == "SliderMultiplier": SliderMultiplier = float(val)
                    elif key == "SliderTickRate": SliderTickRate = float(val)
                    else: print(f"{YELLOW}[WARN] Unknown line format \"{line}\" in [Events] section.{ENDC}")
                    del key, val
                except: return ".osu file format is invalid."
            del line

        elif section[0] == "events": # [Events]
            Breaks = []
            Videos = []
            for line in section[1:]:
                if line[:1] == "//": continue
                val = line.split(",") # For whatever reason peppy made some things a string when they could all just be an int (char) but ok maybe im missing something? this section is weird shit

                if val[0] == '0':
                    BackgroundFileName = val[2]
                elif val[0] == '2':
                    Breaks.append(f"{val[1]}:{val[2]}") # Append start to end.
                elif val[0] == 'Video':
                    Videos.append([val[1], val[2]]) # StartTime, filename (w/ extension)
                else: print(f"{YELLOW}[WARN] Unknown line format \"{line}\" in [Events] section.{ENDC}")# TODO: will have to add ;continue here if we continue doing anything beyond this point!
                # TODO Storyboards, bg colours, videos, etc.
                del val
            del line

        elif section[0] == "timingpoints": # [TimingPoints]
            TimingPoints = []
            for _point in section[1:]:

                point        = _point.split(",")

                if len(point) != 8:
                    print(f"{YELLOW}[WARN] Could not parse point \"{_point}\" in [TimingPoints] section.{ENDC}")
                    continue

                offset       = int(point[0])
                ms_per_beat  = float(point[1])
                meter        = int(point[2])
                sample_set   = int(point[3])
                sample_index = int(point[4])
                volume       = int(point[5])
                inherited    = bool(point[6])
                kiai_mode    = bool(point[7])
                del point

                TimingPoints.append({"Offset": offset, "MSPerBeat": ms_per_beat, "Meter": meter,
                                    "SampleSet": sample_set, "Volume": volume,
                                    "Inherited": inherited,"KiaiMode": kiai_mode})

                del offset, ms_per_beat,  \
                    meter, sample_set,    \
                    sample_index, volume, \
                    inherited, kiai_mode
            del _point

        elif section[0] == "colours": # [Colours]
            Colours = []#? no checks
            for line in section[1:]:
                if ": " in line: key, val = line.split(": ")
                else: print(f"{YELLOW}[WARN] Unknown line format \"{line}\" in [Colours] section.{ENDC}");continue

                Colours.append({key: val})
                del key, val
            del line

        elif section[0] == "hitobjects": # [HitObjects]
            HitObjects = [] # TODO: ACTUALLY unpack "extras" everywhere! .split(":")!@!@!@@ TODO: actually just make a function?
            for line in section[1:]:
                split = line.split(",")#? this whole section #?
                split_len = len(split)
                x, y, object_time, object_type, hitSound = split[:5] # standard for every object type

                if int(object_type) & 1: # Hitcircle
                    circle_start_time = time.time()

                    # 5, 6 with extras.
                    if split_len not in (5,6): print(f"{YELLOW}[WARN] FAILED HITCIRCLE - \"{split}\" in [HitObjects] section.{ENDC}");continue

                    if split_len == 6:
                        extras = split[5]
                        HitObjects.append({"x": x, "y": y, "time": object_time, "type": object_type, "hitSound": hitSound, "extras": extras})
                        del extras
                    else: HitObjects.append({"x": x, "y": y, "time": object_time, "type": object_type, "hitSound": hitSound})

                    if debug: print(f"{PINK}READ HITCIRCLE{ENDC} Time taken: {'%.3f' % round((time.time() - circle_start_time) * 1000000, 3)} microseconds.")
                    del circle_start_time

                elif int(object_type) & 2: # Slider
                    slider_start_time = time.time()
                    if split_len not in (8, 11):print(f"{YELLOW}[WARN] FAILED SLIDER - \"{split}\" in [HitObjects] section.{ENDC}");del slider_start_time;continue#?

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
                    if split_len != 7:#?
                        del spinner_start_time
                        print(f"{YELLOW}[WARN] FAILED SPINNER - \"{split}\" in [HitObjects] section.{ENDC}");continue

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
            del line
        del section
    del SECTIONS

    # Now that we have fully parsed our beatmap and assigned values, let's return them all.
    BeatmapData = {
        "General": {
            "AudioFilename": AudioFilename,
            "AudioLeadIn": AudioLeadIn,
            "PreviewTime": PreviewTime,
            "Countdown": Countdown,
            "SampleSet": SampleSet,
            "StackLeniency": StackLeniency,
            "Mode": Mode,
            "LetterboxInBreaks": LetterboxInBreaks,
            "WidescreenStoryboard": WidescreenStoryboard,
            "SpecialStyle": SpecialStyle,
            "UseSkinSprites": UseSkinSprites
        },
        "Editor": {
            "Bookmarks": Bookmarks,
            "DistanceSpacing": DistanceSpacing,
            "BeatDivisor": BeatDivisor,
            "GridSize": GridSize,
            "TimelineZoom": TimelineZoom
        },
        "Metadata": {
            "Title": Title,
            "TitleUnicode": TitleUnicode,
            "Artist": Artist,
            "ArtistUnicode": ArtistUnicode,
            "Creator": Creator,
            "Version": Version,
            "Source": Source,
            "Tags": Tags,
            "BeatmapID": BeatmapID,
            "BeatmapSetID": BeatmapSetID
        },
        "Difficulty": {
            "HPDrainRate": HPDrainRate,
            "CircleSize": CircleSize,
            "OsuPixels": osu_pixels(CircleSize), # Not directly from beatmap, but probably useful? TODO: Add it as an option.
            "OverallDifficulty": OverallDifficulty,
            "ApproachRate": ApproachRate,
            "SliderMultiplier": SliderMultiplier,
            "SliderTickRate": SliderTickRate
        },
        "Events": {
            "BackgroundFileName": BackgroundFileName,
            "Breaks": Breaks,
            "Videos": Videos
        },
        "TimingPoints": TimingPoints,
        "Colours": Colours,
        "HitObject": HitObjects
    }

    # Just return literally everything we've done.
    # Since we memory handle properly, it returns only the relevant data.
    return BeatmapData


""" And for users using our program directly.. """

if __name__ == "__main__":
    filename = input(f"{CYAN}What is the name of the .osu file (Include extension)?{ENDC}\n>> ")
    start_full_time = time.time()
    BeatmapData = None
    with open(filename, "r") as f:
        BeatmapData = ParseBeatmap(0, f)
    if BeatmapData: print(f"{CYAN}DONE. Time taken: {'%.3f' % round((time.time() - start_full_time) * 1000, 1)} milliseconds.{ENDC}")
    else: print(f"{RED}[ERR] {BeatmapData}.{ENDC}")