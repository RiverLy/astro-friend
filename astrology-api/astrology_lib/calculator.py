"""
AstrologyCalculator - Main class for calculating astrological charts.
"""

import logging
from typing import Optional, Union, List, Dict, Any
from datetime import datetime

from kerykeion import (
    AstrologicalSubject,
    KerykeionChartSVG,
    SynastryAspects,
    NatalAspects,
    RelationshipScoreFactory,
    CompositeSubjectFactory,
)
from kerykeion.settings.config_constants import DEFAULT_ACTIVE_POINTS, DEFAULT_ACTIVE_ASPECTS
from kerykeion.kr_types.kr_models import ActiveAspect
from kerykeion.kr_types.kr_literals import (
    KerykeionChartTheme,
    KerykeionChartLanguage,
    Planet,
    AxialCusps,
)

from .types.request_models import SubjectModel, TransitSubjectModel
from .utils.get_time_from_google import get_time_from_google

logger = logging.getLogger(__name__)

GEONAMES_ERROR_MESSAGE = (
    "City/Nation name error or invalid GeoNames username. "
    "Please check your username or city name and try again. "
    "You can create a free username here: https://www.geonames.org/login/. "
    "If you want to bypass the usage of GeoNames, please remove the geonames_username field from the request. "
    "Note: The nation field should be the country code (e.g. US, UK, FR, DE, etc.)."
)


class AstrologyCalculator:
    """
    Main calculator class for astrological chart calculations.
    """

    def _create_astrological_subject(
        self,
        subject: Union[SubjectModel, TransitSubjectModel],
    ) -> AstrologicalSubject:
        """
        Helper method to create an AstrologicalSubject from a SubjectModel.
        
        Args:
            subject: SubjectModel or TransitSubjectModel instance
            
        Returns:
            AstrologicalSubject instance
            
        Raises:
            ValueError: If geonames lookup fails
        """
        try:
            return AstrologicalSubject(
                name=subject.name,
                year=subject.year,
                month=subject.month,
                day=subject.day,
                hour=subject.hour,
                minute=subject.minute,
                city=subject.city,
                nation=subject.nation,
                lat=subject.latitude,
                lng=subject.longitude,
                tz_str=subject.timezone,
                zodiac_type=subject.zodiac_type,  # type: ignore
                sidereal_mode=subject.sidereal_mode,
                houses_system_identifier=subject.houses_system_identifier,  # type: ignore
                perspective_type=subject.perspective_type,  # type: ignore
                geonames_username=subject.geonames_username,
                online=True if subject.geonames_username else False,
            )
        except Exception as e:
            if "data found for this city" in str(e):
                raise ValueError(GEONAMES_ERROR_MESSAGE) from e
            raise

    def get_birth_data(self, subject: SubjectModel) -> Dict[str, Any]:
        """
        Retrieve astrological data for a specific birth date.
        Does not include the chart nor the aspects.
        
        Args:
            subject: SubjectModel with birth information
            
        Returns:
            Dictionary with status and birth data
            
        Raises:
            ValueError: If geonames lookup fails or invalid input
            Exception: For other calculation errors
        """
        logger.debug(f"Getting birth data for: {subject.name}")
        
        astrological_subject = self._create_astrological_subject(subject)
        data = astrological_subject.model().model_dump()
        
        return {
            "status": "OK",
            "data": data,
        }

    def calculate_birth_chart(
        self,
        subject: SubjectModel,
        theme: Optional[KerykeionChartTheme] = "classic",
        language: Optional[KerykeionChartLanguage] = "EN",
        wheel_only: Optional[bool] = False,
        active_points: Optional[List[Union[Planet, AxialCusps]]] = None,
        active_aspects: Optional[List[ActiveAspect]] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve an astrological birth chart for a specific birth date.
        Includes the data for the subject and the aspects.
        
        Args:
            subject: SubjectModel with birth information
            theme: Chart theme (classic, light, dark, dark-high-contrast)
            language: Chart language (EN, FR, PT, ES, TR, RU, IT, CN, DE, HI)
            wheel_only: If True, only the zodiac wheel will be returned
            active_points: List of active points to display
            active_aspects: List of active aspects to display
            
        Returns:
            Dictionary with status, chart SVG, data, and aspects
            
        Raises:
            ValueError: If geonames lookup fails or invalid input
            Exception: For other calculation errors
        """
        logger.debug(f"Calculating birth chart for: {subject.name}")
        
        astrological_subject = self._create_astrological_subject(subject)
        data = astrological_subject.model().model_dump()
        
        kerykeion_chart = KerykeionChartSVG(
            astrological_subject,
            theme=theme,
            chart_language=language or "EN",
            active_points=active_points or DEFAULT_ACTIVE_POINTS,
            active_aspects=active_aspects or DEFAULT_ACTIVE_ASPECTS,
        )
        
        if wheel_only:
            svg = kerykeion_chart.makeWheelOnlyTemplate(minify=True)
        else:
            svg = kerykeion_chart.makeTemplate(minify=True)
        
        return {
            "status": "OK",
            "chart": svg,
            "data": data,
            "aspects": [aspect.model_dump() for aspect in kerykeion_chart.aspects_list],
        }

    def get_natal_aspects(
        self,
        subject: SubjectModel,
        active_points: Optional[List[Union[Planet, AxialCusps]]] = None,
        active_aspects: Optional[List[ActiveAspect]] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve natal aspects and data for a specific subject.
        Does not include the chart.
        
        Args:
            subject: SubjectModel with birth information
            active_points: List of active points to display
            active_aspects: List of active aspects to display
            
        Returns:
            Dictionary with status, data, and aspects
            
        Raises:
            ValueError: If geonames lookup fails or invalid input
            Exception: For other calculation errors
        """
        logger.debug(f"Getting natal aspects for: {subject.name}")
        
        astrological_subject = self._create_astrological_subject(subject)
        
        aspects = NatalAspects(
            astrological_subject,
            active_points=active_points or DEFAULT_ACTIVE_POINTS,
            active_aspects=active_aspects or DEFAULT_ACTIVE_ASPECTS,
        ).relevant_aspects
        
        return {
            "status": "OK",
            "data": {"subject": astrological_subject.model().model_dump()},
            "aspects": [aspect.model_dump() for aspect in aspects],
        }

    def calculate_synastry_chart(
        self,
        first_subject: SubjectModel,
        second_subject: SubjectModel,
        theme: Optional[KerykeionChartTheme] = "classic",
        language: Optional[KerykeionChartLanguage] = "EN",
        wheel_only: Optional[bool] = False,
        active_points: Optional[List[Union[Planet, AxialCusps]]] = None,
        active_aspects: Optional[List[ActiveAspect]] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve a synastry chart between two subjects.
        Includes the data for the subjects and the aspects.
        
        Args:
            first_subject: First SubjectModel
            second_subject: Second SubjectModel
            theme: Chart theme
            language: Chart language
            wheel_only: If True, only the zodiac wheel will be returned
            active_points: List of active points to display
            active_aspects: List of active aspects to display
            
        Returns:
            Dictionary with status, chart SVG, data, and aspects
            
        Raises:
            ValueError: If geonames lookup fails or invalid input
            Exception: For other calculation errors
        """
        logger.debug(f"Calculating synastry chart for: {first_subject.name} and {second_subject.name}")
        
        first_astrological_subject = self._create_astrological_subject(first_subject)
        second_astrological_subject = self._create_astrological_subject(second_subject)
        
        kerykeion_chart = KerykeionChartSVG(
            first_astrological_subject,
            second_obj=second_astrological_subject,
            chart_type="Synastry",
            theme=theme,
            chart_language=language or "EN",
            active_points=active_points or DEFAULT_ACTIVE_POINTS,
            active_aspects=active_aspects or DEFAULT_ACTIVE_ASPECTS,
        )
        
        if wheel_only:
            svg = kerykeion_chart.makeWheelOnlyTemplate(minify=True)
        else:
            svg = kerykeion_chart.makeTemplate(minify=True)
        
        return {
            "status": "OK",
            "chart": svg,
            "aspects": [aspect.model_dump() for aspect in kerykeion_chart.aspects_list],
            "data": {
                "first_subject": first_astrological_subject.model().model_dump(),
                "second_subject": second_astrological_subject.model().model_dump(),
            },
        }

    def get_synastry_aspects(
        self,
        first_subject: SubjectModel,
        second_subject: SubjectModel,
        active_points: Optional[List[Union[Planet, AxialCusps]]] = None,
        active_aspects: Optional[List[ActiveAspect]] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve synastry aspects between two subjects.
        Does not include the chart.
        
        Args:
            first_subject: First SubjectModel
            second_subject: Second SubjectModel
            active_points: List of active points to display
            active_aspects: List of active aspects to display
            
        Returns:
            Dictionary with status, data, and aspects
            
        Raises:
            ValueError: If geonames lookup fails or invalid input
            Exception: For other calculation errors
        """
        logger.debug(f"Getting synastry aspects for: {first_subject.name} and {second_subject.name}")
        
        first_astrological_subject = self._create_astrological_subject(first_subject)
        second_astrological_subject = self._create_astrological_subject(second_subject)
        
        aspects = SynastryAspects(
            first_astrological_subject,
            second_astrological_subject,
            active_points=active_points or DEFAULT_ACTIVE_POINTS,
            active_aspects=active_aspects or DEFAULT_ACTIVE_ASPECTS,
        ).relevant_aspects
        
        return {
            "status": "OK",
            "data": {
                "first_subject": first_astrological_subject.model().model_dump(),
                "second_subject": second_astrological_subject.model().model_dump(),
            },
            "aspects": [aspect.model_dump() for aspect in aspects],
        }

    def calculate_transit_chart(
        self,
        first_subject: SubjectModel,
        transit_subject: TransitSubjectModel,
        theme: Optional[KerykeionChartTheme] = "classic",
        language: Optional[KerykeionChartLanguage] = "EN",
        wheel_only: Optional[bool] = False,
        active_points: Optional[List[Union[Planet, AxialCusps]]] = None,
        active_aspects: Optional[List[ActiveAspect]] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve a transit chart for a specific subject.
        Includes the data for the subject and the aspects.
        
        Args:
            first_subject: SubjectModel for the natal chart
            transit_subject: TransitSubjectModel for the transit time
            theme: Chart theme
            language: Chart language
            wheel_only: If True, only the zodiac wheel will be returned
            active_points: List of active points to display
            active_aspects: List of active aspects to display
            
        Returns:
            Dictionary with status, chart SVG, data, and aspects
            
        Raises:
            ValueError: If geonames lookup fails or invalid input
            Exception: For other calculation errors
        """
        logger.debug(f"Calculating transit chart for: {first_subject.name}")
        
        first_astrological_subject = self._create_astrological_subject(first_subject)
        
        second_astrological_subject = AstrologicalSubject(
            name="Transit",
            year=transit_subject.year,
            month=transit_subject.month,
            day=transit_subject.day,
            hour=transit_subject.hour,
            minute=transit_subject.minute,
            city=transit_subject.city,
            nation=transit_subject.nation,
            lat=transit_subject.latitude,
            lng=transit_subject.longitude,
            tz_str=transit_subject.timezone,
            zodiac_type=first_astrological_subject.zodiac_type,  # type: ignore
            sidereal_mode=first_subject.sidereal_mode,
            houses_system_identifier=first_subject.houses_system_identifier,  # type: ignore
            perspective_type=first_subject.perspective_type,  # type: ignore
            geonames_username=transit_subject.geonames_username,
            online=True if transit_subject.geonames_username else False,
        )
        
        kerykeion_chart = KerykeionChartSVG(
            first_astrological_subject,
            second_obj=second_astrological_subject,
            chart_type="Transit",
            theme=theme,
            chart_language=language or "EN",
            active_points=active_points or DEFAULT_ACTIVE_POINTS,
            active_aspects=active_aspects or DEFAULT_ACTIVE_ASPECTS,
        )
        
        if wheel_only:
            svg = kerykeion_chart.makeWheelOnlyTemplate(minify=True)
        else:
            svg = kerykeion_chart.makeTemplate(minify=True)
        
        return {
            "status": "OK",
            "chart": svg,
            "aspects": [aspect.model_dump() for aspect in kerykeion_chart.aspects_list],
            "data": {
                "subject": first_astrological_subject.model().model_dump(),
                "transit": second_astrological_subject.model().model_dump(),
            },
        }

    def get_transit_aspects(
        self,
        first_subject: SubjectModel,
        transit_subject: TransitSubjectModel,
        active_points: Optional[List[Union[Planet, AxialCusps]]] = None,
        active_aspects: Optional[List[ActiveAspect]] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve transit aspects and data for a specific subject.
        Does not include the chart.
        
        Args:
            first_subject: SubjectModel for the natal chart
            transit_subject: TransitSubjectModel for the transit time
            active_points: List of active points to display
            active_aspects: List of active aspects to display
            
        Returns:
            Dictionary with status, data, and aspects
            
        Raises:
            ValueError: If geonames lookup fails or invalid input
            Exception: For other calculation errors
        """
        logger.debug(f"Getting transit aspects for: {first_subject.name}")
        
        first_astrological_subject = self._create_astrological_subject(first_subject)
        
        second_astrological_subject = AstrologicalSubject(
            name="Transit",
            year=transit_subject.year,
            month=transit_subject.month,
            day=transit_subject.day,
            hour=transit_subject.hour,
            minute=transit_subject.minute,
            city=transit_subject.city,
            nation=transit_subject.nation,
            lat=transit_subject.latitude,
            lng=transit_subject.longitude,
            tz_str=transit_subject.timezone,
            zodiac_type=first_astrological_subject.zodiac_type,  # type: ignore
            sidereal_mode=first_subject.sidereal_mode,
            houses_system_identifier=first_subject.houses_system_identifier,  # type: ignore
            perspective_type=first_subject.perspective_type,  # type: ignore
            geonames_username=transit_subject.geonames_username,
            online=True if transit_subject.geonames_username else False,
        )
        
        aspects = SynastryAspects(
            first_astrological_subject,
            second_astrological_subject,
            active_points=active_points or DEFAULT_ACTIVE_POINTS,
            active_aspects=active_aspects or DEFAULT_ACTIVE_ASPECTS,
        ).relevant_aspects
        
        return {
            "status": "OK",
            "data": {
                "subject": first_astrological_subject.model().model_dump(),
                "transit": second_astrological_subject.model().model_dump(),
            },
            "aspects": [aspect.model_dump() for aspect in aspects],
        }

    def calculate_relationship_score(
        self,
        first_subject: SubjectModel,
        second_subject: SubjectModel,
    ) -> Dict[str, Any]:
        """
        Calculates the relevance of the relationship between two subjects
        using the Ciro Discepolo method.
        
        Results:
            - 0 to 5: Minimal relationship
            - 5 to 10: Medium relationship
            - 10 to 15: Important relationship
            - 15 to 20: Very important relationship
            - 20 to 35: Exceptional relationship
            - 30 and above: Rare Exceptional relationship
        
        Args:
            first_subject: First SubjectModel
            second_subject: Second SubjectModel
            
        Returns:
            Dictionary with status, score, score_description, is_destiny_sign, aspects, and data
            
        Raises:
            ValueError: If geonames lookup fails or invalid input
            Exception: For other calculation errors
        """
        logger.debug(f"Calculating relationship score for: {first_subject.name} and {second_subject.name}")
        
        first_astrological_subject = self._create_astrological_subject(first_subject)
        second_astrological_subject = self._create_astrological_subject(second_subject)
        
        score_factory = RelationshipScoreFactory(first_astrological_subject, second_astrological_subject)
        score_model = score_factory.get_relationship_score()
        
        return {
            "status": "OK",
            "score": score_model.score_value,
            "score_description": score_model.score_description,
            "is_destiny_sign": score_model.is_destiny_sign,
            "aspects": [aspect.model_dump() for aspect in score_model.aspects],
            "data": {
                "first_subject": first_astrological_subject.model().model_dump(),
                "second_subject": second_astrological_subject.model().model_dump(),
            },
        }

    def calculate_composite_chart(
        self,
        first_subject: SubjectModel,
        second_subject: SubjectModel,
        theme: Optional[KerykeionChartTheme] = "classic",
        language: Optional[KerykeionChartLanguage] = "EN",
        wheel_only: Optional[bool] = False,
        active_points: Optional[List[Union[Planet, AxialCusps]]] = None,
        active_aspects: Optional[List[ActiveAspect]] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve a composite chart between two subjects.
        Includes the data for the subjects and the aspects.
        The method used is the midpoint method.
        
        Args:
            first_subject: First SubjectModel
            second_subject: Second SubjectModel
            theme: Chart theme
            language: Chart language
            wheel_only: If True, only the zodiac wheel will be returned
            active_points: List of active points to display
            active_aspects: List of active aspects to display
            
        Returns:
            Dictionary with status, chart SVG, data, and aspects
            
        Raises:
            ValueError: If geonames lookup fails or invalid input
            Exception: For other calculation errors
        """
        logger.debug(f"Calculating composite chart for: {first_subject.name} and {second_subject.name}")
        
        first_astrological_subject = self._create_astrological_subject(first_subject)
        second_astrological_subject = self._create_astrological_subject(second_subject)
        
        composite_factory = CompositeSubjectFactory(first_astrological_subject, second_astrological_subject)
        composite_subject = composite_factory.get_midpoint_composite_subject_model()
        
        kerykeion_chart = KerykeionChartSVG(
            composite_subject,
            chart_type="Composite",
            theme=theme,
        )
        
        if wheel_only:
            svg = kerykeion_chart.makeWheelOnlyTemplate(minify=True)
        else:
            svg = kerykeion_chart.makeTemplate(minify=True)
        
        composite_subject_dict = composite_subject.model_dump()
        for key in ["first_subject", "second_subject"]:
            if key in composite_subject_dict:
                composite_subject_dict.pop(key)
        
        return {
            "status": "OK",
            "chart": svg,
            "aspects": [aspect.model_dump() for aspect in kerykeion_chart.aspects_list],
            "data": {
                "composite_subject": composite_subject_dict,
                "first_subject": first_astrological_subject.model().model_dump(),
                "second_subject": second_astrological_subject.model().model_dump(),
            },
        }

    def get_composite_aspects(
        self,
        first_subject: SubjectModel,
        second_subject: SubjectModel,
        active_points: Optional[List[Union[Planet, AxialCusps]]] = None,
        active_aspects: Optional[List[ActiveAspect]] = None,
    ) -> Dict[str, Any]:
        """
        Retrieves the data and the aspects for a composite chart between two subjects.
        Does not include the chart.
        
        Args:
            first_subject: First SubjectModel
            second_subject: Second SubjectModel
            active_points: List of active points to display
            active_aspects: List of active aspects to display
            
        Returns:
            Dictionary with status, data, and aspects
            
        Raises:
            ValueError: If geonames lookup fails or invalid input
            Exception: For other calculation errors
        """
        logger.debug(f"Getting composite aspects for: {first_subject.name} and {second_subject.name}")
        
        first_astrological_subject = self._create_astrological_subject(first_subject)
        second_astrological_subject = self._create_astrological_subject(second_subject)
        
        composite_factory = CompositeSubjectFactory(first_astrological_subject, second_astrological_subject)
        composite_data = composite_factory.get_midpoint_composite_subject_model()
        
        aspects = NatalAspects(
            composite_data,
            active_points=active_points or DEFAULT_ACTIVE_POINTS,
            active_aspects=active_aspects or DEFAULT_ACTIVE_ASPECTS,
        ).relevant_aspects
        
        composite_subject_dict = composite_data.model_dump()
        for key in ["first_subject", "second_subject"]:
            if key in composite_subject_dict:
                composite_subject_dict.pop(key)
        
        return {
            "status": "OK",
            "data": {
                "composite_subject": composite_subject_dict,
                "first_subject": first_astrological_subject.model().model_dump(),
                "second_subject": second_astrological_subject.model().model_dump(),
            },
            "aspects": [aspect.model_dump() for aspect in aspects],
        }

    def get_current_time_data(self) -> Dict[str, Any]:
        """
        Retrieve astrological data for the current moment.
        
        Returns:
            Dictionary with status and birth data for current UTC time
            
        Raises:
            Exception: If unable to get current time or calculate chart
        """
        logger.debug("Getting current astrological data")
        
        try:
            utc_datetime = get_time_from_google()
            datetime_dict = {
                "year": utc_datetime.year,  # type: ignore
                "month": utc_datetime.month,  # type: ignore
                "day": utc_datetime.day,  # type: ignore
                "hour": utc_datetime.hour,  # type: ignore
                "minute": utc_datetime.minute,  # type: ignore
                "second": utc_datetime.second,  # type: ignore
            }
        except Exception as e:
            logger.error(f"Failed to get current time: {e}")
            raise
        
        logger.debug(f"Current UTC time: {datetime_dict}")
        
        try:
            today_subject = AstrologicalSubject(
                city="GMT",
                nation="UK",
                lat=51.477928,
                lng=-0.001545,
                tz_str="GMT",
                year=datetime_dict["year"],
                month=datetime_dict["month"],
                day=datetime_dict["day"],
                hour=datetime_dict["hour"],
                minute=datetime_dict["minute"],
                online=False,
            )
            
            return {
                "status": "OK",
                "data": today_subject.model().model_dump(),
            }
        except Exception as e:
            logger.error(f"Failed to calculate current time chart: {e}")
            raise

