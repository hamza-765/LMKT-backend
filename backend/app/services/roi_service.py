from __future__ import annotations

from app.schemas.roi import ROIRequest, ROIResponse


class ROIService:
    """Frontend-compatible ROI calculator for LMKT enterprise scenarios."""

    _BASE_RULES: dict[str, dict[str, dict[str, int | str]]] = {
        "Energy": {
            "Large": {"estimated_roi": 38, "annual_savings": 150000, "utility_efficiency": 27, "implementation_time": "6 months"},
            "Medium": {"estimated_roi": 30, "annual_savings": 90000, "utility_efficiency": 22, "implementation_time": "4 months"},
            "Small": {"estimated_roi": 22, "annual_savings": 45000, "utility_efficiency": 16, "implementation_time": "3 months"},
        },
        "Utilities": {
            "Large": {"estimated_roi": 36, "annual_savings": 140000, "utility_efficiency": 26, "implementation_time": "6 months"},
            "Medium": {"estimated_roi": 28, "annual_savings": 80000, "utility_efficiency": 21, "implementation_time": "4 months"},
            "Small": {"estimated_roi": 21, "annual_savings": 38000, "utility_efficiency": 15, "implementation_time": "3 months"},
        },
    }

    _SECTOR_FACTORS: dict[str, float] = {
        "Energy": 1.0,
        "Utilities": 0.95,
        "Public Sector / E-Gov": 1.15,
    }

    _SIZE_FACTORS: dict[str, float] = {
        "Small": 0.85,
        "Medium": 1.0,
        "Large": 1.15,
    }

    _MODULE_WEIGHTS: dict[str, float] = {
        "gis integration": 0.12,
        "security management": 0.10,
        "managed services": 0.08,
    }

    def calculate(self, payload: ROIRequest) -> ROIResponse:
        """Return the ROI estimate with frontend-style derived metrics."""
        sector = self._normalize_sector(payload.sector)
        organization_size = self._normalize_organization_size(payload.organization_size)

        base_rule = self._BASE_RULES.get(sector, {}).get(organization_size)
        if not base_rule:
            base_rule = {
                "estimated_roi": 20,
                "annual_savings": 50000,
                "utility_efficiency": 14,
                "implementation_time": "4 months",
            }

        annual_savings = int(base_rule["annual_savings"])
        utility_efficiency = int(base_rule["utility_efficiency"])
        estimated_roi = int(base_rule["estimated_roi"])
        implementation_time = str(base_rule["implementation_time"])

        efficiency_gain = self._calculate_efficiency_gain(
            sector=sector,
            organization_size=organization_size,
            utility_efficiency=utility_efficiency,
            modules=payload.modules,
        )
        digital_transformation_velocity = self._calculate_transformation_velocity(
            sector=sector,
            organization_size=organization_size,
            modules=payload.modules,
        )
        projected_savings = self._calculate_projected_savings(
            annual_savings=annual_savings,
            sector=sector,
            organization_size=organization_size,
            modules=payload.modules,
        )

        return ROIResponse(
            estimated_roi=estimated_roi,
            annual_savings=annual_savings,
            utility_efficiency=utility_efficiency,
            implementation_time=implementation_time,
            efficiency_gain=efficiency_gain,
            digital_transformation_velocity=digital_transformation_velocity,
            projected_savings=projected_savings,
            extras={
                "sector": sector,
                "organization_size": organization_size,
                "modules": [module.strip() for module in payload.modules if module.strip()],
            },
        )

    @staticmethod
    def _normalize_sector(sector: str) -> str:
        """Normalize the sector into the same canonical labels used by the rules."""
        normalized = sector.strip().title()
        if normalized == "Public Sector / E-Gov":
            return "Public Sector / E-Gov"
        return normalized

    @staticmethod
    def _normalize_organization_size(organization_size: str | None) -> str:
        """Normalize organization size into the same size bands used by the UI."""
        if organization_size is None:
            return "Large"

        normalized = organization_size.strip().title()
        if normalized in {"Small", "Medium", "Large"}:
            return normalized

        if normalized.startswith("100"):
            return "Small"
        if normalized.startswith("3"):
            return "Medium"
        return "Large"

    def _calculate_efficiency_gain(
        self,
        *,
        sector: str,
        organization_size: str,
        utility_efficiency: int,
        modules: list[str],
    ) -> int:
        """Compute the frontend-aligned efficiency gain percentage."""
        sector_factor = self._SECTOR_FACTORS.get(sector, 1.0)
        size_factor = self._SIZE_FACTORS.get(organization_size, 1.0)
        module_weight = self._sum_module_weights(modules)

        gain = (utility_efficiency * 0.9) * sector_factor * size_factor + (module_weight * 100)
        return max(1, round(gain))

    def _calculate_transformation_velocity(
        self,
        *,
        sector: str,
        organization_size: str,
        modules: list[str],
    ) -> float:
        """Compute the frontend-aligned velocity multiplier."""
        sector_factor = self._SECTOR_FACTORS.get(sector, 1.0)
        size_factor = self._SIZE_FACTORS.get(organization_size, 1.0)
        module_weight = self._sum_module_weights(modules)

        velocity = 1.4 + (sector_factor * 0.8) + (size_factor * 0.7) + (module_weight * 2.0)
        return round(velocity, 1)

    def _calculate_projected_savings(
        self,
        *,
        annual_savings: int,
        sector: str,
        organization_size: str,
        modules: list[str],
    ) -> dict[str, int]:
        """Build the yearly projected savings chart values used by the UI."""
        sector_factor = self._SECTOR_FACTORS.get(sector, 1.0)
        size_factor = self._SIZE_FACTORS.get(organization_size, 1.0)
        module_weight = self._sum_module_weights(modules)

        year_1 = round(annual_savings * (0.42 + (module_weight * 0.5) + (sector_factor - 1) * 0.15))
        year_2 = round(annual_savings * (0.62 + (module_weight * 0.6) + (size_factor - 1) * 0.25))
        year_3 = round(annual_savings * (0.82 + (module_weight * 0.7) + (size_factor - 1) * 0.35))

        return {
            "year_1": max(1, year_1),
            "year_2": max(1, year_2),
            "year_3": max(1, year_3),
        }

    def _sum_module_weights(self, modules: list[str]) -> float:
        """Normalize and sum frontend toggle weights into a single multiplier."""
        normalized_modules = [module.strip().lower() for module in modules if module and module.strip()]
        return sum(self._MODULE_WEIGHTS.get(module, 0.0) for module in normalized_modules)
