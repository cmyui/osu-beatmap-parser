import os
from time import time


class TimingPoint(object):
    def __init__(self, offset, ms_per_beat, meter, sample_set,
                 sample_index, volume, inherited, kiai_mode):
        self.offset = offset
        self.ms_per_beat = ms_per_beat
        self.meter = meter
        self.sample_set = sample_set
        self.sample_index = sample_index
        self.volume = volume
        self.inherited = inherited
        self.kiai_mode = kiai_mode


class HitObject(object):
    def __init__(self, x, y, time, hit_sound, extras):
        self.x = x
        self.y = y
        self.time = time
        self.hit_sound = hit_sound
        self.extras = extras


class Break(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end


class Video(object):
    def __init__(self, start, filename):
        self.start = start
        self.filename = filename


class Colour(object):
    def __init__(self, combo, r, g, b):
        self.combo = combo
        self.red = r
        self.green = g
        self.blue = b


class Beatmap(object):
    def __init__(self, beatmap_data):
        self._offset = 0
        self._debug = 0

        # General
        self.audio_filename = None
        self.audio_leadin = 0
        self.preview_time = 0
        self.countdown = 0
        self.sampleset = None
        self.stack_leniency = 0.0
        self.mode = 0
        self.letterbox_in_breaks = 0
        self.story_fire_in_front = 0
        self.skin_preference = None
        self.epilepsy_warning = 0
        self.countdown_offset = 0
        self.widescreen_storyboard = 0
        self.special_style = 0
        self.use_skin_sprites = 0

        # Editor
        self.bookmarks = []
        self.distance_spacing = 0.0
        self.beat_divisor = 0
        self.grid_size = 0
        self.timeline_zoom = 0.0

        # Metadata
        self.title = None
        self.title_unicode = None
        self.artist = None
        self.artist_unicode = None
        self.creator = None
        self.version = None
        self.source = None
        self.tags = []# list?
        self.beatmap_id = 0
        self.beatmapset_id = 0

        # Difficulty
        self.hp_drain_rate = 0.0
        self.circle_size = 0.0
        self.overall_difficulty = 0.0
        self.approach_rate = 0.0
        self.slider_multiplier = 0.0
        self.slider_tickrate = 0.0

        # Events
        self.background = None
        self.breaks = []
        #TODO: storyboards

        # Colours
        self.colours = []

        # Hitobjects and timingpoints
        self.timing_points = None
        self.hit_objects = None
        self.parse_beatmap_and_initialize_fields(beatmap_data)
    
    def parse_beatmap_and_initialize_fields(self, beatmap_data):
        # Simple
        self.parse_general_section(beatmap_data)
        self.parse_editor_section(beatmap_data)
        self.parse_metadata_section(beatmap_data)
        self.parse_difficulty_section(beatmap_data)
        self.parse_events_section(beatmap_data)
        #complex
        self.parse_timingpoints_section(beatmap_data)
        #simplest
        self.parse_colours_section(beatmap_data)

        # More complex
        self.parse_hitobject_section(beatmap_data)
    
    def parse_general_section(self, beatmap_data):
        for idx, line in enumerate(beatmap_data):
            if not line or line[0] == "[": break # New section found

            key, val = line.split(": ").strip()

            if key == "AudioFilename": self.audio_filename = str(val)
            elif key == "AudioLeadIn": self.audio_leadin = int(val)
            elif key == "PreviewTime": self.preview_time = int(val)
            elif key == "Countdown": self.countdown = int(val)
            elif key == "SampleSet": self.sampleset = str(val)
            elif key == "StackLeniency": self.stack_leniency = float(val)
            elif key == "Mode": self.mode = int(val)
            elif key == "LetterboxInBreaks": self.letterbox_in_breaks = bool(val)
            elif key == "WidescreenStoryboard": self.widescreen_storyboard = bool(val)
            elif key == "SpecialStyle": self.special_style = bool(val)
            elif key == "UseSkinSprites": self.use_skin_sprites = bool(val)
            else: print(f"{YELLOW}[WARN] Unknown key \"{key}\" in [General] section.{ENDC}")

        self._offset += idx

    def parse_events_section(self, beatmap_data):
        for idx, line in enumerate(beatmap_data[self._offset:]):
            if not line or line[0] == "[": break # New section found
            
            key, val = line.split(": ")
            if key == "Bookmarks": self.bookmarks = val.split(",")
            elif key == "DistanceSpacing": self.distance_spacing = float(val)
            elif key == "BeatDivisor": self.beat_divisor = int(val)
            elif key == "GridSize": self.grid_size = int(val)
            elif key == "TimelineZoom": self.timeline_zoom = float(val)
            else: print(f"{YELLOW}[WARN] Unknown key \"{key}\" in [Editor] section.{ENDC}")

        self._offset =+ idx
            
    def parse_metadata_section(self, beatmap_data):
        for idx, line in enumerate(beatmap_data[self._offset:]):
            if not line or line[0] == "[": break # New section found
            
            key, val = line.split(":")
            if key == "Title": self.title = str(val)
            elif key == "TitleUnicode": self.title_unicode = str(val)
            elif key == "Artist": self.artist = str(val)
            elif key == "ArtistUnicode": self.artist_unicode = str(val)
            elif key == "Creator": self.creator = str(val)
            elif key == "Version": self.version = str(val)
            elif key == "Source": self.source = str(val)
            elif key == "Tags": self.tags = str(val)
            elif key == "BeatmapID": self.beatmap_id = int(val)
            elif key == "BeatmapSetID": self.beatmapset_id = int(val)
            else: print(f"{YELLOW}[WARN] Unknown key \"{key}\" in [Metadata] section.{ENDC}")
        self._offset += idx
    
    def parse_difficulty_section(self, beatmap_data):
        for idx, line in enumerate(beatmap_data[self._offset:]):
            if not line or line[0] == "[": break # neww sec
            key, val = line.split(":")

            if key == "HPDrainRate": self.hp_drain_rate = float(val)
            elif key == "CircleSize": self.circle_size = float(val)
            elif key == "OverallDifficulty": self.overall_difficulty = float(val)
            elif key == "ApproachRate": self.approach_rate = float(val)
            elif key == "SliderMultiplier": self.slider_multiplier = float(val)
            elif key == "SliderTickRate": self.slider_tickrate = float(val)
            else: print(f"{YELLOW}[WARN] Unknown line format \"{line}\" in [Events] section.{ENDC}")
        self._offset += idx

    def parse_events_section(self, beatmap_data):
        for idx, line in enumerate(beatmap_data[self._offset:]):
            if not line or line[0] == "[": break # new sec
            if line[:2] == "//": continue
            
            val = line.split(",")

            if val[0] == '0': self.background = val[2]
            elif val[0] == '2':
                self.breaks = Break(int(val[1]), int(val[2]))
            elif val[0] == 'Video': Video(int(val[1], str(val[2])))
            # TODO: storyboard, bg colors, etc.
        self._offset += idx

    # Timing points?

    def parse_colours_section(self, beatmap_data):
        for idx, line in enumerate(beatmap_data[self._offset:]):
            if not line or line[0] == "[": break # ne wsec
            key, val = line.split(": ")
            _RED, _GREEN, _BLUE = val.split(",")

            self.colours.append(Colour(str(key), int(_RED), int(_GREEN), int(_BLUE)))

        self._offset += idx

    # Hit objects?
""" Now for our functions. """

def osu_pixels(cs):
    """
    Calculate "osu!pixels" from our circle size.
    """

    return 54.4 - 4.48 * cs


def ParseBeatmap(fileText, file=None, IncludeEditor=False):
    """
    Parse the full beatmap given.
    This function is a mess of a memory map!

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
                if line[:2] == "//": continue
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

            self.timing_points = [[TimingPoint(int(point[0]), float(point[1]), int(point[2]), int(point[3]), int(point[4]), int(point[5]), bool(point[6]), bool(point[7])) for point in _point.split(",")] for _point in section[1:]]
            """
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
            """

        elif section[0] == "colours": # [Colours]
            Colours = []#? no checks
            for line in section[1:]:
                if ": " in line: key, val = line.split(": ")
                else: print(f"{YELLOW}[WARN] Unknown line format \"{line}\" in [Colours] section.{ENDC}");continue

                Colours.append({key: val})
                del key, val
            del line

        elif section[0] == "hitobjects": # [HitObjects]
            #TODO
            #self.timing_points = [[TimingPoint(int(point[0]), float(point[1]), int(point[2]), int(point[3]), int(point[4]), int(point[5]), bool(point[6]), bool(point[7])) for point in _point.split(",")] for _point in section[1:]]

            HitObjects = [] # TODO: ACTUALLY unpack "extras" everywhere! .split(":")!@!@!@@ TODO: actually just make a function?
            for line in section[1:]:
                split = line.split(",")#? this whole section #?
                split_len = len(split)
                x, y, object_time, object_type, hitSound = split[:5] # standard for every object type

                if int(object_type) & 1: # Hitcircle
                    circle_start_time = time()

                    # 5, 6 with extras.
                    if split_len not in (5,6): print(f"{YELLOW}[WARN] FAILED HITCIRCLE - \"{split}\" in [HitObjects] section.{ENDC}");continue

                    if split_len == 6:
                        extras = split[5]
                        HitObjects.append({"x": x, "y": y, "time": object_time, "type": object_type, "hitSound": hitSound, "extras": extras})
                        del extras
                    else: HitObjects.append({"x": x, "y": y, "time": object_time, "type": object_type, "hitSound": hitSound})

                    if debug: print(f"{PINK}READ HITCIRCLE{ENDC} Time taken: {'%.3f' % round((time() - circle_start_time) * 1000000, 3)} microseconds.")
                    del circle_start_time

                elif int(object_type) & 2: # Slider
                    slider_start_time = time()
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

                    if debug: print(f"{GREEN}READ SLIDER{ENDC} Time taken: {'%.3f' % round((time() - slider_start_time) * 1000000, 3)} microseconds.")
                    del slider_start_time

                elif int(object_type) & 8: # Spinner
                    spinner_start_time = time()
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
                    if debug: print(f"{YELLOW}READ SPINNER{ENDC} Time taken: {'%.3f' % round((time() - spinner_start_time) * 1000000, 3)} microseconds.")
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
    GREEN  = '\033[92m'
    CYAN   = '\033[96m'
    PINK   = '\033[95m'
    YELLOW = '\033[93m'
    RED    = '\033[91m'
    ENDC   = '\033[0m'
    import sys

    filename = sys.argv[1] if len(sys.argv) > 1 else input(f"{CYAN}What is the name of the .osu file (Include extension)?{ENDC}\n>> ")
    start_full_time = time()
    BeatmapData = None
    with open(filename, "r") as f:
        BeatmapData = ParseBeatmap(0, f)

    if not BeatmapData: print(f"{RED}[ERR] {BeatmapData}.{ENDC}")
    elif debug: print(f"{CYAN}DONE. Time taken: {'%.3f' % round((time() - start_full_time) * 1000, 1)} milliseconds.{ENDC}")
    else: print(BeatmapData)

def parse_beatmap(beatmap_data):
    return Beatmap(beatmap_data.splitlines())

def parse_beatmap_file(beatmap_path):
    with open(beatmap_path, 'r') as f:
        data = f.read()
    return parse_beatmap(data)