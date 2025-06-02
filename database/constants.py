color_schemes = [
    {
        "type": "dark",
        "maze": {
            "color_bg": (10, 10, 10),
            "color_end_dot": (255, 0, 85),
            "color_solution": (0, 255, 255),
            "color_start_dot": (0, 255, 0),
            "color_wall": (136, 136, 136),
        },
        "video": {
            "bg_color": (10, 10, 10),
            "strap_color": (180, 180, 180),
            "text_color": (255, 255, 255),
        },
    },
    {
        "type": "dark",
        "maze": {
            "color_bg": (17, 17, 27),
            "color_end_dot": (255, 48, 48),
            "color_solution": (255, 204, 0),
            "color_start_dot": (0, 255, 127),
            "color_wall": (122, 122, 160),
        },
        "video": {
            "bg_color": (17, 17, 27),
            "strap_color": (150, 150, 190),
            "text_color": (255, 255, 255),
        },
    },
    {
        "type": "light",
        "maze": {
            "color_bg": (249, 249, 249),
            "color_end_dot": (198, 40, 40),
            "color_solution": (25, 118, 210),
            "color_start_dot": (86, 185, 90),  # Lighter green
            "color_wall": (51, 51, 51),
        },
        "video": {
            "bg_color": (249, 249, 249),
            "strap_color": (80, 80, 80),
            "text_color": (26, 26, 26),
        },
    },
    {
        "type": "dark",
        "maze": {
            "color_bg": (18, 18, 18),
            "color_end_dot": (80, 221, 255),  # Lighter cyan/blue
            "color_solution": (255, 69, 0),
            "color_start_dot": (255, 255, 51),
            "color_wall": (176, 176, 176),
        },
        "video": {
            "bg_color": (18, 18, 18),
            "strap_color": (60, 180, 60),
            "text_color": (57, 255, 20),
        },
    },
    {
        "type": "dark",
        "maze": {
            "color_bg": (0, 0, 0),
            "color_end_dot": (211, 47, 47),
            "color_solution": (170, 0, 255),  # Vibrant purple
            "color_start_dot": (96, 202, 100),  # Lighter green
            "color_wall": (178, 178, 178),
        },
        "video": {
            "bg_color": (0, 0, 0),
            "strap_color": (160, 160, 160),
            "text_color": (227, 227, 227),
        },
    },
]
color_schemes.extend(
    [
        {
            "type": "light",
            "maze": {
                "color_bg": (252, 246, 235),  # Light cream
                "color_end_dot": (25, 80, 187),  # Deep blue
                "color_solution": (220, 20, 60),  # Vibrant crimson
                "color_start_dot": (46, 139, 87),  # Medium green
                "color_wall": (139, 69, 19),  # Brown
            },
            "video": {
                "bg_color": (252, 246, 235),
                "strap_color": (139, 69, 19),
                "text_color": (50, 50, 50),
            },
        },
        {
            "type": "light",
            "maze": {
                "color_bg": (235, 245, 251),  # Pale blue
                "color_end_dot": (200, 30, 30),  # Red
                "color_solution": (106, 13, 173),  # Vibrant purple
                "color_start_dot": (34, 139, 34),  # Forest green
                "color_wall": (25, 25, 112),  # Navy blue
            },
            "video": {
                "bg_color": (235, 245, 251),
                "strap_color": (70, 70, 120),
                "text_color": (25, 25, 70),
            },
        },
        {
            "type": "light",
            "maze": {
                "color_bg": (230, 250, 240),  # Light mint
                "color_end_dot": (220, 60, 20),  # Orange-red
                "color_solution": (0, 100, 200),  # Bright blue
                "color_start_dot": (20, 60, 190),  # Deep blue
                "color_wall": (0, 100, 100),  # Dark teal
            },
            "video": {
                "bg_color": (230, 250, 240),
                "strap_color": (20, 110, 110),
                "text_color": (30, 30, 30),
            },
        },
        {
            "type": "light",
            "maze": {
                "color_bg": (255, 255, 255),
                "color_wall": (0, 0, 0),
                "color_solution": (255, 0, 0),
                "color_start_dot": (0, 200, 0),
                "color_end_dot": (0, 0, 200),
            },
            "video": {
                "bg_color": (0, 0, 0),
                "strap_color": (255, 255, 0),
                "text_color": (0, 0, 0),
            },
        },
        {
            "type": "dark",
            "maze": {
                "color_bg": (0, 0, 0),
                "color_wall": (255, 255, 255),
                "color_solution": (255, 0, 0),
                "color_start_dot": (0, 200, 0),
                "color_end_dot": (0, 0, 200),
            },
            "video": {
                "bg_color": (0, 0, 0),
                "strap_color": (255, 255, 0),
                "text_color": (0, 0, 0),
            },
        },
    ]
)

font_schemes = [
    {
        "text_font": ["video_editor/fonts/Benton Modern Text Bold.otf", 90],
        "timer_font": ["video_editor/fonts/BebasNeue-Regular.ttf", 100],
        "cta_font": ["video_editor/fonts/Benton Modern D SemiBold Italic.otf", 85],
    },
    {
        "text_font": ["video_editor/fonts/BebasNeue-Regular.ttf", 90],
        "timer_font": ["video_editor/fonts/ShareTechMono-Regular.ttf", 85],
        "cta_font": ["video_editor/fonts/Merriweather_120pt-SemiBoldItalic.ttf", 85],
    },
    {
        "text_font": ["video_editor/fonts/Anton-Regular.ttf", 90],
        "timer_font": ["video_editor/fonts/Orbitron-ExtraBold.ttf", 75],
        "cta_font": ["video_editor/fonts/PlayfairDisplay-Italic.ttf", 85],
    },
    {
        "text_font": ["video_editor/fonts/Oswald-Regular.ttf", 90],
        "timer_font": ["video_editor/fonts/VT323-Regular.ttf", 100],
        "cta_font": ["video_editor/fonts/LibreBaskerville-Italic.ttf", 85],
    },
    {
        "text_font": ["video_editor/fonts/LeagueSpartan-Bold.otf", 90],
        "timer_font": ["video_editor/fonts/Rajdhani-Bold.ttf", 100],
        "cta_font": ["video_editor/fonts/Cormorant-BoldItalic.ttf", 85],
    },
    {
        "text_font": ["video_editor/fonts/impact.ttf", 90],
        "timer_font": ["video_editor/fonts/IBMPlexMono-Bold.ttf", 75],
        "cta_font": ["video_editor/fonts/DancingScript-Medium.ttf", 85],
    },
    {
        "text_font": ["video_editor/fonts/Staatliches-Regular.ttf", 90],
        "timer_font": ["video_editor/fonts/Inconsolata_Condensed-Bold.ttf", 100],
        "cta_font": ["video_editor/fonts/Lora-Italic.ttf", 85],
    },
    {
        "text_font": ["video_editor/fonts/AbrilFatface-Regular.ttf", 90],
        "timer_font": ["video_editor/fonts/PressStart2P-Regular.ttf", 45],
        "cta_font": ["video_editor/fonts/GreatVibes-Regular.ttf", 85],
    },
    {
        "text_font": ["video_editor/fonts/Righteous-Regular.ttf", 90],
        "timer_font": ["video_editor/fonts/Audiowide-Regular.ttf", 75],
        "cta_font": ["video_editor/fonts/Pacifico-Regular.ttf", 85],
    },
    {
        "text_font": ["video_editor/fonts/Poppins-ExtraBold.ttf", 90],
        "timer_font": ["video_editor/fonts/SourceCodePro-Black.ttf", 75],
        "cta_font": ["video_editor/fonts/CinzelDecorative-Regular.ttf", 85],
    },
    {
        "text_font": ["video_editor/fonts/Bangers-Regular.ttf", 90],
        "timer_font": ["video_editor/fonts/NovaMono-Regular.ttf", 75],
        "cta_font": ["video_editor/fonts/Satisfy-Regular.ttf", 85],
    },
]
