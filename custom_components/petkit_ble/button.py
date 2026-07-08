"""Button platform for Petkit BLE integration."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PetkitBLECoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Petkit BLE buttons."""
    coordinator: PetkitBLECoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        PetkitFilterResetButton(coordinator),
    ]
    
    async_add_entities(entities)


class PetkitButtonBase(CoordinatorEntity[PetkitBLECoordinator], ButtonEntity):
    """Base class for Petkit buttons."""

    def __init__(self, coordinator: PetkitBLECoordinator) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        # Device info will be provided by the dynamic property

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info dynamically."""
        device_id = self.coordinator.device.serial if self.coordinator.device.serial != "Uninitialized" else self.coordinator.address
        device_name = self.coordinator.device.name_readable if self.coordinator.device.name_readable != "Uninitialized" else "Water Fountain"
        return {
            "identifiers": {(DOMAIN, device_id)},
            "name": device_name,
            "manufacturer": "Petkit",
            "model": self.coordinator.device.product_name or "Water Fountain",
            "sw_version": str(self.coordinator.device.firmware) if self.coordinator.device.firmware else "Unknown",
        }

class PetkitFilterResetButton(PetkitButtonBase):
    """Button to reset the filter life."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:rotate-left"

    def __init__(self, coordinator: PetkitBLECoordinator) -> None:
        """Initialize the filter reset button."""
        super().__init__(coordinator)
        device_id = coordinator.device.serial if coordinator.device.serial != "Uninitialized" else coordinator.address.replace(":", "")
        self._attr_unique_id = f"{device_id}_reset_filter"
        self._attr_name = "Reset Filter Life"

    async def async_press(self) -> None:
        """Handle the button press to reset the filter."""
        await self.coordinator.async_reset_filter()
        await self.coordinator.async_request_refresh()