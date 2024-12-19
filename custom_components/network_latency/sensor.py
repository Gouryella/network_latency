from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.event import async_track_time_interval
from ping3 import ping
from datetime import timedelta
import logging
from . import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config, async_add_entities):
    name = config.data.get("name")
    ip = config.data.get("ip")
    scan_interval = config.data.get("scan_interval", DEFAULT_SCAN_INTERVAL)

    sensor = NetworkLatencySensor(name, ip, scan_interval)
    async_add_entities([sensor])


class NetworkLatencySensor(SensorEntity):

    def __init__(self, name, ip, scan_interval):
        self._name = name
        self._ip = ip
        self._state = None
        self._scan_interval = scan_interval
        self._unsub_update = None
        self._unit_of_measurement = "ms"
        self._attr_icon = "mdi:network"

    @property
    def name(self):
        return f"Ping {self._name}"

    @property
    def unique_id(self):
        return f"ping_{self._name.lower()}"
    
    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        if self._state == "Timeout":
            return "mdi:alert-circle"
        elif self._state == "Error":
            return "mdi:alert"
        return self._attr_icon
    
    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement
    
    async def async_added_to_hass(self):
        _LOGGER.info(f"Starting ping sensor for {self._name} ({self._ip})")
        self._unsub_update = async_track_time_interval(
            self.hass, self.async_update, timedelta(seconds=self._scan_interval)
        )

    async def async_will_remove_from_hass(self):
        if self._unsub_update:
            self._unsub_update()
        _LOGGER.info(f"Stopping ping sensor for {self._name} ({self._ip})")

    async def async_update(self, now=None):
        try:
            latency = ping(self._ip, timeout=1) 
            if latency is not None:
                self._state = round(latency * 1000, 2) 
            elif latency == 0:
                self._state = "Timeout"
            else:
                self._state = "Timeout"
        except Exception as e: 
            _LOGGER.error(f"Ping to {self._ip} ({self._name}) failed: {e}")
            self._state = "Error"
