import argparse
import logging

from PIL import Image
import numpy as np
from evernote.api.client import EvernoteClient
from evernote.edam.error.ttypes import EDAMUserException, EDAMSystemException, EDAMErrorCode
from evernote.edam.notestore.ttypes import NoteFilter
from wordcloud import WordCloud

DEFAULT_IMAGE_FILE = "EvernoteTagCloud.png"
DEFAULT_IMAGE_SIZE = "2048x1152"
DEFAULT_MAX_TAGS = "300"
DEFAULT_HORIZONTAL_TAGS = "0.90"
DEFAULT_TAG_SCALING = "0.50"
DEFAULT_COLOR_SCHEME = "Blues"

VERSION = "0.1.0"
MATPLOTLIB_COLORMAPS = ['viridis', 'plasma', 'inferno', 'magma', 'Greys', 'Purples', 'Blues', 'Greens', 'Oranges',
                        'Reds', 'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu', 'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn',
                        'BuGn', 'YlGn', 'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink', 'spring', 'summer',
                        'autumn', 'winter', 'cool', 'Wistia', 'hot', 'afmhot', 'gist_heat', 'copper', 'PiYG', 'PRGn',
                        'BrBG', 'PuOr', 'RdGy', 'RdBu', 'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic',
                        'Pastel1', 'Pastel2', 'Paired', 'Accent', 'Dark2', 'Set1', 'Set2', 'Set3', 'tab10', 'tab20',
                        'tab20b', 'tab20c', 'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern', 'gnuplot',
                        'gnuplot2', 'CMRmap', 'cubehelix', 'brg', 'hsv', 'gist_rainbow', 'rainbow', 'jet',
                        'nipy_spectral', 'gist_ncar']


def setup_logging():
    """Configures logging level"""
    logging.basicConfig(level=logging.INFO)

def print_version():
    print("EvernoteTagCloud.py", VERSION)

def command_line_args():
    """Uses ArgumentParser to retrieve pre-parsed command line arguments

    Returns:
        argparse.Namespace with the parsed command line arguments
    """
    parser = argparse.ArgumentParser(description='Create Word Cloud from Evernote Tags')
    parser.add_argument("--verbose", action="store_true", help="print tag names and frequency")
    parser.add_argument("--sandbox", action="store_true", help="connect to Evernote sandbox environment")
    parser.add_argument("--imageFile", default=DEFAULT_IMAGE_FILE, type=argparse.FileType('wb'), help="tag cloud file (default: " + DEFAULT_IMAGE_FILE + ")")
    parser.add_argument("--imageSize", default=DEFAULT_IMAGE_SIZE, help="tag cloud size (default: " + DEFAULT_IMAGE_SIZE + ")")
    parser.add_argument("--maskFile", default=None, type=argparse.FileType('rb'), help="image mask file to use")
    parser.add_argument("--fontFile", default=None, type=argparse.FileType('rb'), help="tag font to use")
    parser.add_argument("--maxTags", default=DEFAULT_MAX_TAGS, type=int, help="maximum number of tags (default: " + DEFAULT_MAX_TAGS + ")")
    parser.add_argument("--horizontalTags", default=DEFAULT_HORIZONTAL_TAGS, type=float, help="ratio of horizontal tags (default: " + DEFAULT_HORIZONTAL_TAGS + ")")
    parser.add_argument("--tagScaling", default=DEFAULT_TAG_SCALING, type=float, help="impact of tag frequency on tag size (default: " + DEFAULT_TAG_SCALING + ")")
    parser.add_argument("--tagColorScheme", default=DEFAULT_COLOR_SCHEME, choices=MATPLOTLIB_COLORMAPS, help="tag color scheme (default: " + DEFAULT_COLOR_SCHEME + ")")
    parser.add_argument("evernoteAuthToken", help="authentication token for Evernote API")
    return parser.parse_args()


def parse_args(args):
    """Parses and validates command line arguments

    Args:
        args (argparse.Namespace): Pre-paresed command line arguments

    Returns:
        bool: verbose flag, indicates whether tag frequency dictionary should be printed
        bool: sandbox flag, indicates whether Evernote API calls should be made against the production or sandbox environment
        str: name of the file the tag cloud image should be saved to
        int: width of the tag cloud image
        int: height of the tag cloud image
        file: mask file to use when generating the tag cloud
        str: font file to use when generating the tag cloud
        int: maximum number of tags to include in the tag cloud
        int: ratio of horizontal tags in the tag cloud
        int: the impact of tag frequency (as opposed to tag ranking) on tag size
        str: the name of a matplotlib colormap to use for tag colors (see https://matplotlib.org/examples/color/colormaps_reference.html for available colormaps)
        str: the Evernote API authentication token

    Raises:
        ValueError: if numeric parameters have an invalid value
    """
    image_width_height = args.imageSize.split("x")
    if len(image_width_height) != 2:
        raise ValueError("invalid imageSize [%s] format, expected format is <width>x<height>", args.imageSize)

    image_width, image_height = int(image_width_height[0]), int(image_width_height[1])
    if image_width not in range(10, 10000):
        raise ValueError("invalid imageSize.width [%d], imageSize.width must be between 10 and 9999", image_width)

    if image_height not in range(10, 10000):
        raise ValueError("invalid imageSize.height [%d], imageSize.height must be between 10 and 9999", image_height)

    if args.maxTags not in range(1, 1000):
        raise ValueError("invalid maxTags [%d], maxTags must be between 1 and 999", args.maxTags)

    if args.horizontalTags < 0 or args.horizontalTags > 1 :
        raise ValueError("invalid horizontalTags [%f], horizontalTags must be between 0 and 1", args.horizontalTags)

    if args.tagScaling < 0 or args.tagScaling > 1:
        raise ValueError("invalid tagScaling [%f], tagScaling must be between 0 and 1", args.horizontalTags)

    font_file = None if args.fontFile == None else args.fontFile.name

    return args.verbose, args.sandbox, args.imageFile.name, image_width, image_height, args.maskFile, font_file, args.maxTags, args.horizontalTags, args.tagScaling, args.tagColorScheme, args.evernoteAuthToken


def retrieve_tags_and_note_collection_counts(auth_token, sandbox, note_filter):
    """Uses the Evernote API to retrieve tags and note collection counts

    Args:
        auth_token (str): the Evernote API authentication token
        sandbox (bool): sandbox flag, indicates whether Evernote API calls should be made against the production or sandbox environment
        note_filter (evernote.edam.notestore.ttypes.NoteFilter): the filter applied to the search query on the Evernote API

    Returns:
        evernote.edam.type.ttypes.Tag: list of tags in the Evernote acccount
        evernote.edam.notestore.ttypes.NoteCollectionCounts: number of notes for each notebook and tag with a non-zero set of applicable notes
    """
    try:
        client = EvernoteClient(token=auth_token, sandbox=sandbox)
        user_store = client.get_user_store()
        user = user_store.getUser()
        logging.info("Retrieving tags and noteCollectionCounts for Evernote user [%s]%s", user.username, " from sandbox environment" if sandbox else "")

        note_store = client.get_note_store()
        tags = note_store.listTags()
        note_collection_counts = note_store.findNoteCounts(note_filter, False)
        logging.info("Retrieved [%d] tags and [%d] noteCollectionCounts from Notes of user [%s]", len(tags), len(note_collection_counts.tagCounts), user.username)

        return tags, note_collection_counts
    except EDAMSystemException as e:
        logging.error("Failed to retrieve tags and noteCollectionCounts from Evernote API: %s", EDAMErrorCode._VALUES_TO_NAMES[e.errorCode])
        raise
    except EDAMUserException as e:
        logging.error("Failed to retrieve tags and noteCollectionCounts from Evernote API: %s", EDAMErrorCode._VALUES_TO_NAMES[e.errorCode])
        raise


def determine_tag_counts(tags, note_collection_counts):
    """Converts the tags and note collection counts returned by the Evernote API to a tag frequency dictionary

    Args:
        tags (evernote.edam.type.ttypes.Tag): list of tags in the Evernote acccount
        note_collection_counts (evernote.edam.notestore.ttypes.NoteCollectionCounts): number of notes for each notebook and tag with a non-zero set of applicable notes

    Returns:
        dict: tag frequency dictionary
    """
    tag_counts = {}

    guid_tags = {tag.guid: tag for tag in tags}
    for tag_guid in note_collection_counts.tagCounts:
        tag_count = note_collection_counts.tagCounts[tag_guid]
        tag_name = guid_tags[tag_guid].name
        tag_counts[tag_name] = tag_count

    return tag_counts


def generate_tag_cloud(image_width, image_height, max_tags, horizontal_tags, tag_scaling, tag_color_scheme, mask_file, font_file, tag_counts, verbose):
    """Passes the tag frequency dictionary into the word_cloud library to generate a tag cloud

    Args:
        image_width (int): width of the tag cloud image in pixel (only used when mask_file is None)
        image_height (int): height of the tag cloud image in pixel (only used when mask_file is None)
        max_tags (int): the maximum number of tags to include in the tag cloud
        horizontal_tags (int): ratio of horizontal tags in the tag cloud
        tag_scaling (int): the impact of tag frequency (as opposed to tag ranking) on tag size
        tag_color_scheme (str): the name of a matplotlib colormap to use for tag colors (see https://matplotlib.org/examples/color/colormaps_reference.html for available colormaps)
        mask_file (file): the image mask file to use when generating the tag cloud
        mask_file (str): the font to use when generating the tag cloud
        tag_counts (dict): tag frequency dictionary
        verbose (bool): indicates whether tag frequency dictionary should be printed

    Returns:
        wordcloud.wordcloud.WordCloud: the tag cloud from the tag frequency dictionary with the specified settings
    """
    if verbose:
        logging.info(tag_counts)

    tags = max_tags if max_tags < len(tag_counts) else len(tag_counts)

    if mask_file != None:
        logging.info("Generating tag cloud with [%d] tags with mask...", tags)
        mask = np.array(Image.open(mask_file))
        return WordCloud(prefer_horizontal=horizontal_tags, max_words=max_tags, relative_scaling=tag_scaling, colormap=tag_color_scheme, mask=mask, font_path=font_file).generate_from_frequencies(tag_counts)
    else:
        logging.info("Generating tag cloud with [%d] tags...", tags)
        return WordCloud(width=image_width, height=image_height, prefer_horizontal=horizontal_tags, max_words=max_tags, relative_scaling=tag_scaling, colormap=tag_color_scheme, font_path=font_file).generate_from_frequencies(tag_counts)


def save_tag_cloud(tag_cloud, image_file):
    """Uses the word_cloud library to save the tag cloud to an image file

    Args:
        tag_cloud (wordcloud.wordcloud.WordCloud): the tag cloud from the tag frequency dictionary with the specified settings
        image_file (str): name of the file the tag cloud image should be saved to
    """
    logging.info("Saving tag cloud to file [%s]...", image_file)
    tag_cloud.to_file(image_file)


def main():
    """Generates tag cloud using the Evernote API and word_cloud library"""
    setup_logging()
    print_version()
    args = command_line_args()
    verbose, sandbox, image_file, image_width, image_height, mask_file, font_file, max_tags, horizontal_tags, tag_scaling, tag_color_scheme, evernote_auth_token = parse_args(args)
    tags, note_collection_counts = retrieve_tags_and_note_collection_counts(evernote_auth_token, sandbox, NoteFilter())
    tag_counts = determine_tag_counts(tags, note_collection_counts)
    tag_cloud = generate_tag_cloud(image_width, image_height, max_tags, horizontal_tags, tag_scaling, tag_color_scheme, mask_file, font_file, tag_counts, verbose)
    save_tag_cloud(tag_cloud, image_file)


if __name__ == '__main__':
    main()