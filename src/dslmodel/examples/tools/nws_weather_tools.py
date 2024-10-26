import httpx
from pydantic import Field

from dslmodel import DSLModel
from dslmodel.mixins.tools import ToolMixin
from typing import List, Optional


class PointDataProperties(DSLModel):
    """
    Represents the properties returned by the NWS Points API for a specific location.
    """

    forecast: str = Field(
        ...,
        alias="forecast",
        description="URL to retrieve the general forecast for the location."
    )
    forecast_hourly: str = Field(
        ...,
        alias="forecastHourly",
        description="URL to retrieve the hourly forecast for the location."
    )
    forecast_grid_data: str = Field(
        ...,
        alias="forecastGridData",
        description="URL to retrieve grid-based forecast data for the location."
    )
    grid_id: str = Field(
        ...,
        alias="gridId",
        description="Identifier for the Weather Forecast Office (WFO) responsible for the location."
    )
    grid_x: int = Field(
        ...,
        alias="gridX",
        description="The X-coordinate of the grid point used for fetching the forecast."
    )
    grid_y: int = Field(
        ...,
        alias="gridY",
        description="The Y-coordinate of the grid point used for fetching the forecast."
    )


class PointData(DSLModel):
    """
    Represents the complete response from the NWS Points API.
    """

    properties: PointDataProperties = Field(
        ...,
        description="Contains detailed properties related to the forecast endpoints and grid information."
    )


class ForecastPeriod(DSLModel):
    """
    Represents a single forecast period within the gridpoint forecast data.
    """

    number: int = Field(
        ...,
        description="Sequential number indicating the period in the forecast sequence."
    )
    name: str = Field(
        ...,
        description="Name of the forecast period (e.g., 'Tonight', 'Wednesday')."
    )
    start_time: str = Field(
        ...,
        alias="startTime",
        description="ISO 8601 formatted start time of the forecast period."
    )
    end_time: str = Field(
        ...,
        alias="endTime",
        description="ISO 8601 formatted end time of the forecast period."
    )
    temperature: int = Field(
        ...,
        description="Forecasted temperature for the period."
    )
    temperature_unit: str = Field(
        ...,
        alias="temperatureUnit",
        description="Unit of the temperature (e.g., 'F' for Fahrenheit)."
    )
    wind_speed: str = Field(
        ...,
        alias="windSpeed",
        description="Forecasted wind speed (e.g., '10 mph')."
    )
    wind_direction: str = Field(
        ...,
        alias="windDirection",
        description="Forecasted wind direction (e.g., 'NW')."
    )
    icon: str = Field(
        ...,
        description="URL to an icon representing the forecasted conditions."
    )
    short_forecast: str = Field(
        ...,
        alias="shortForecast",
        description="Brief summary of the forecast conditions."
    )
    detailed_forecast: str = Field(
        ...,
        alias="detailedForecast",
        description="Detailed narrative description of the forecast conditions."
    )


class GridpointForecastProperties(DSLModel):
    """
    Contains forecast periods and additional metadata for a specific grid point.
    """

    periods: List[ForecastPeriod] = Field(
        ...,
        description="List of forecast periods detailing the weather conditions."
    )


class GridpointForecast(DSLModel):
    """
    Represents the complete response from the NWS Gridpoint Forecast API.
    """

    properties: GridpointForecastProperties = Field(
        ...,
        description="Contains forecast periods and related metadata for the grid point."
    )


class NWSWeatherTools(ToolMixin):
    BASE_URL = "https://api.weather.gov"

    def get_point_data(self, latitude: float, longitude: float) -> PointData:
        """
        Fetch point data for a specific latitude and longitude.
        """
        url = f"{self.BASE_URL}/points/{latitude},{longitude}"
        headers = {
            'User-Agent': 'YourAppName/1.0 (your.email@example.com)'  # Replace with your info
        }
        with httpx.Client(headers=headers) as client:
            response = client.get(url)
            response.raise_for_status()
            return PointData(**response.json())

    def get_gridpoint_forecast(self, grid_id: str, grid_x: int, grid_y: int) -> GridpointForecast:
        """
        Fetch forecast data for a specific grid point.
        """
        url = f"{self.BASE_URL}/gridpoints/{grid_id}/{grid_x},{grid_y}/forecast"
        headers = {
            'User-Agent': 'YourAppName/1.0 (your.email@example.com)'  # Replace with your info
        }
        with httpx.Client(headers=headers) as client:
            response = client.get(url)
            response.raise_for_status()
            return GridpointForecast(**response.json())

    def get_forecast_by_location(self, latitude: float, longitude: float) -> List[ForecastPeriod]:
        """
        Combined method to get forecast periods by latitude and longitude.
        """
        point_data = self.get_point_data(latitude, longitude)
        grid_id = point_data.properties.grid_id
        grid_x = point_data.properties.grid_x
        grid_y = point_data.properties.grid_y
        forecast = self.get_gridpoint_forecast(grid_id, grid_x, grid_y)
        return forecast.properties.periods


def main():
    """Main function"""
    from dslmodel import init_instant

    init_instant()

    # Example usage
    weather_tools = NWSWeatherTools()

    # Example coordinates for New York City
    latitude = 40.7128
    longitude = -74.0060

    forecast_periods = weather_tools(prompt="Get me the forcast by location", latitude=latitude, longitude=longitude, verbose=True)

    try:
    #     forecast_periods = weather_tools.get_forecast_by_location(latitude, longitude)
        for period in forecast_periods:
            print(f"{period.name}: {period.short_forecast} with a temperature of {period.temperature}{period.temperature_unit}")
    except httpx.HTTPStatusError as e:
        print(f"An error occurred while fetching weather data: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    main()
