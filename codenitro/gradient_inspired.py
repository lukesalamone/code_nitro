from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, Number, Operator, Generic

class GradientInspiredStyle(Style):
    background_color = "#ffffff"  # White background for clarity
    default_style = ""

    styles = {
        Comment:              'italic #2DAEA1',   # Seafoam
        Keyword:              'bold #3AAFA8',    # Aqua Green
        Name:                 '#5EB0BA',        # Pale Teal
        String:               'italic #75B0B2', # Soft Lilac
        Error:                'bg:#CC3333 #ffffff',
        Number:               '#98B3DC',        # Periwinkle
        Operator:             '#BDCAF0',        # Lavender
        Generic.Heading:      'bold #86B2D1',   # Light Blue
        Generic.Subheading:   'bold #AAB3E6',   # Light Purple
        Generic.Emph:         'italic #D9B4F7', # Soft Lilac
    }

# Save this style to a Python file (e.g., gradient_inspired.py) and use it in Pygments with the appropriate command.
