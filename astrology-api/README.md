# Astrology Library

A Python library for calculating astrological charts using Kerykeion. This library provides accurate birth charts, synastry charts, transit charts, and composite charts with SVG generation and compatibility scores.

## Features

- **Birth Charts**: Generate complete birth charts with planetary positions and aspects
- **Synastry Charts**: Compare two subjects and show their interactions and compatibility
- **Transit Charts**: Show current planetary influences for a subject
- **Composite Charts**: Compute composite charts using the midpoint method
- **Relationship Scores**: Calculate compatibility scores using the Ciro Discepolo method
- **SVG Chart Generation**: Generate beautiful SVG charts with multiple themes
- **Multiple Languages**: Support for 10 languages (EN, FR, PT, ES, TR, RU, IT, CN, DE, HI)
- **Multiple Themes**: Light, dark, dark-high-contrast, and classic themes
- **Flexible Configuration**: Support for different zodiac types, house systems, and perspectives

## Installation

```bash
pip install -e .
```

Or using pipenv:

```bash
pipenv install
```

## Quick Start

```python
from astrology_lib import AstrologyCalculator, SubjectModel

# Create calculator instance
calculator = AstrologyCalculator()

# Create a subject
subject = SubjectModel(
    name="John Doe",
    year=1980,
    month=12,
    day=12,
    hour=12,
    minute=12,
    city="London",
    nation="GB",
    longitude=0,
    latitude=51.4825766,
    timezone="Europe/London",
    zodiac_type="Tropic"
)

# Get birth data
birth_data = calculator.get_birth_data(subject)
print(birth_data)

# Calculate birth chart with SVG
birth_chart = calculator.calculate_birth_chart(
    subject,
    theme="dark",
    language="EN"
)
print(f"Chart SVG: {birth_chart['chart'][:100]}...")  # First 100 chars
print(f"Aspects: {len(birth_chart['aspects'])} aspects found")
```

## Usage Examples

### Birth Chart

```python
from astrology_lib import AstrologyCalculator, SubjectModel

calculator = AstrologyCalculator()

subject = SubjectModel(
    name="Jane Doe",
    year=1990,
    month=6,
    day=15,
    hour=14,
    minute=30,
    city="New York",
    nation="US",
    longitude=-74.0060,
    latitude=40.7128,
    timezone="America/New_York"
)

# Get birth data only
data = calculator.get_birth_data(subject)

# Get birth chart with SVG
chart = calculator.calculate_birth_chart(
    subject,
    theme="light",
    language="EN",
    wheel_only=False
)

# Get natal aspects only
aspects = calculator.get_natal_aspects(subject)
```

### Synastry Chart

```python
from astrology_lib import AstrologyCalculator, SubjectModel

calculator = AstrologyCalculator()

person1 = SubjectModel(
    name="Person 1",
    year=1985,
    month=3,
    day=20,
    hour=10,
    minute=0,
    city="Paris",
    nation="FR",
    longitude=2.3522,
    latitude=48.8566,
    timezone="Europe/Paris"
)

person2 = SubjectModel(
    name="Person 2",
    year=1990,
    month=7,
    day=15,
    hour=16,
    minute=30,
    city="Berlin",
    nation="DE",
    longitude=13.4050,
    latitude=52.5200,
    timezone="Europe/Berlin"
)

# Calculate synastry chart
synastry = calculator.calculate_synastry_chart(
    person1,
    person2,
    theme="classic",
    language="EN"
)

# Get synastry aspects only
aspects = calculator.get_synastry_aspects(person1, person2)

# Calculate relationship score
score = calculator.calculate_relationship_score(person1, person2)
print(f"Relationship Score: {score['score']}")
print(f"Description: {score['score_description']}")
```

### Transit Chart

```python
from astrology_lib import AstrologyCalculator, SubjectModel, TransitSubjectModel

calculator = AstrologyCalculator()

# Natal subject
natal = SubjectModel(
    name="John",
    year=1980,
    month=1,
    day=1,
    hour=12,
    minute=0,
    city="London",
    nation="GB",
    longitude=0,
    latitude=51.4825766,
    timezone="Europe/London"
)

# Transit time
transit = TransitSubjectModel(
    year=2024,
    month=1,
    day=1,
    hour=12,
    minute=0,
    city="London",
    nation="GB",
    longitude=0,
    latitude=51.4825766,
    timezone="Europe/London"
)

# Calculate transit chart
transit_chart = calculator.calculate_transit_chart(
    natal,
    transit,
    theme="dark"
)

# Get transit aspects only
aspects = calculator.get_transit_aspects(natal, transit)
```

### Composite Chart

```python
from astrology_lib import AstrologyCalculator, SubjectModel

calculator = AstrologyCalculator()

person1 = SubjectModel(...)
person2 = SubjectModel(...)

# Calculate composite chart
composite = calculator.calculate_composite_chart(
    person1,
    person2,
    theme="classic"
)

# Get composite aspects only
aspects = calculator.get_composite_aspects(person1, person2)
```

### Current Time Data

```python
from astrology_lib import AstrologyCalculator

calculator = AstrologyCalculator()

# Get astrological data for current UTC time
current_data = calculator.get_current_time_data()
```

## Configuration Options

### Zodiac Types

- `"Tropic"`: Tropical zodiac (default)
- `"Sidereal"`: Sidereal zodiac (requires `sidereal_mode`)

### House Systems

- `"P"`: Placidus (default)
- `"A"`: Equal
- `"B"`: Alcabitius
- `"C"`: Campanus
- And many more (see Kerykeion documentation)

### Themes

- `"classic"`: Traditional colorful theme (default)
- `"light"`: Modern soft-colored light theme
- `"dark"`: Modern dark theme
- `"dark-high-contrast"`: High-contrast dark theme

### Languages

- `"EN"`: English (default)
- `"FR"`: French
- `"PT"`: Portuguese
- `"ES"`: Spanish
- `"TR"`: Turkish
- `"RU"`: Russian
- `"IT"`: Italian
- `"CN"`: Chinese
- `"DE"`: German
- `"HI"`: Hindi

### Perspective Types

- `"Apparent Geocentric"`: Earth-centered, apparent positions (default)
- `"Heliocentric"`: Sun-centered
- `"Topocentric"`: Observer's specific location
- `"True Geocentric"`: Earth-centered, true positions

## Automatic Coordinates (Geonames)

You can use automatic coordinate lookup by providing a `geonames_username`:

```python
subject = SubjectModel(
    name="John Doe",
    year=1980,
    month=12,
    day=12,
    hour=12,
    minute=12,
    city="Jamaica, New York",
    nation="US",
    geonames_username="YOUR_GEONAMES_USERNAME"
)
```

Note: You need to sign up at [Geonames](https://www.geonames.org/login) to get a free username (up to 10,000 requests per day).

## Relationship Score Interpretation

The relationship score uses the Ciro Discepolo method:

- **0 to 5**: Minimal relationship
- **5 to 10**: Medium relationship
- **10 to 15**: Important relationship
- **15 to 20**: Very important relationship
- **20 to 35**: Exceptional relationship
- **30 and above**: Rare Exceptional relationship

## Error Handling

The library raises standard Python exceptions:

- `ValueError`: For invalid input parameters or geonames lookup failures
- `Exception`: For other calculation errors

```python
from astrology_lib import AstrologyCalculator, SubjectModel

calculator = AstrologyCalculator()

try:
    subject = SubjectModel(...)
    result = calculator.calculate_birth_chart(subject)
except ValueError as e:
    print(f"Invalid input: {e}")
except Exception as e:
    print(f"Calculation error: {e}")
```

## Dependencies

- `kerykeion`: Core astrology calculation library
- `pydantic`: Data validation
- `pytz`: Timezone handling
- `requests`: For time API calls

## License

This library is Free/Libre Open Source Software with an AGPLv3 license.

## Credits

This library is based on [Kerykeion](https://github.com/g-battaglia/kerykeion), a Python library for astrology calculations by Giacomo Battaglia. The underlying tools are built on the Swiss Ephemeris.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
