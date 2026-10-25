"""
Regression tests for market engine fixes.

Tests two confirmed issues:
1. No-comparables crash due to missing ambiguous_availability_count
2. Furnishing breakdown inconsistency (showing candidate pool instead of actual comparison set)
"""

import pytest
import pandas as pd
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

# Load the market engine module
spec = spec_from_file_location(
    "furnishing_market_engine",
    "src/23_furnishing_market_engine.py"
)
market_module = module_from_spec(spec)
spec.loader.exec_module(market_module)

get_furnishing_market_reference = market_module.get_furnishing_market_reference

# Load unified engine
from src.unified_prediction_engine import get_rental_assessment


class TestNoComparablesResultContract:
    """Test that no-comparables return path has consistent result contract."""

    def test_no_comparables_includes_ambiguous_availability_count(self):
        """
        No-comparables result should include ambiguous_availability_count = 0.

        This prevents KeyError crash in unified_prediction_engine.py line 146.
        """
        result = get_furnishing_market_reference(
            target_locality="NonExistentLocality12345",
            target_bhk=10,
            target_size=10000,
            target_furnishing="Furnished"
        )

        # Should have zero comparables
        assert result["listing_count"] == 0

        # Must include ambiguous_availability_count key
        assert "ambiguous_availability_count" in result

        # Should be zero when no comparables exist
        assert result["ambiguous_availability_count"] == 0

        # Other expected keys in no-comparables result
        assert result["furnishing_listing_count"] == 0
        assert result["median_rent"] is None
        assert result["q1_rent"] is None
        assert result["q3_rent"] is None
        assert result["comparison_type"] == "No comparable listings"
        assert result["furnishing_breakdown"] == {}

    def test_unified_engine_handles_no_comparables(self):
        """
        Unified engine should handle no-comparables result without crashing.

        Previously crashed at line 146 trying to access
        market_result["ambiguous_availability_count"].
        """
        # Use impossible parameters that won't match any listing
        result = get_rental_assessment(
            locality="NonExistentLocality12345",
            size_sqft=10000,
            bhk=10,
            bathrooms=10,
            furnishing_status="Furnished"
        )

        # Should complete without KeyError
        assert "market_listing_count" in result
        assert result["market_listing_count"] == 0

        # Should have ambiguous availability count, even if zero
        assert "market_ambiguous_availability_count" in result
        assert result["market_ambiguous_availability_count"] == 0

    def test_defensive_get_in_unified_engine(self, monkeypatch):
        """
        Unified engine should use .get() with default for backward compatibility.

        Even if an older result dict is missing the key, it should not crash.
        """
        # Mock the market engine to return a legacy result without ambiguous_availability_count
        def mock_market_reference(*args, **kwargs):
            # Return a realistic legacy result dict missing the new key
            return {
                "listing_count": 3,
                "furnishing_listing_count": 1,
                "median_rent": 35000.0,
                "q1_rent": 32000.0,
                "q3_rent": 38000.0,
                "median_rent_per_sqft": 28.0,
                "comparison_type": "All-furnishing fallback",
                "sample_quality": "Very limited",
                "lower_size": 2600.0,
                "upper_size": 3900.0,
                "data_refreshed": None,
                "furnishing_breakdown": {"Semi-Furnished": 2, "Unfurnished": 1},
                # Intentionally omit ambiguous_availability_count to test backward compatibility
                "comparables": pd.DataFrame(),
            }

        # Patch the market engine function in the unified_prediction_engine module
        import src.unified_prediction_engine as upe
        monkeypatch.setattr(upe, "get_furnishing_market_reference", mock_market_reference)

        # This should not raise KeyError despite missing key in market result
        result = get_rental_assessment(
            locality="Marathahalli",
            size_sqft=3250,
            bhk=4,
            bathrooms=3,
            furnishing_status="Furnished"
        )

        # Should have the key with default value of 0
        assert "market_ambiguous_availability_count" in result
        assert result["market_ambiguous_availability_count"] == 0
        assert isinstance(result["market_ambiguous_availability_count"], int)


class TestFurnishingBreakdownConsistency:
    """Test that furnishing breakdown reflects actual comparison set."""

    def test_furnishing_specific_breakdown_matches_selected(self):
        """
        When using furnishing-specific comparison, breakdown should match
        the actual selected comparables, not the broader candidate pool.

        Previously, breakdown was calculated from all comparables before
        furnishing-specific selection, causing inconsistent counts.
        """
        # Whitefield 2 BHK Semi-Furnished has enough comparables
        result = get_furnishing_market_reference(
            target_locality="Whitefield",
            target_bhk=2,
            target_size=1200,
            target_furnishing="Semi-Furnished",
            min_furnishing_comparables=4
        )

        # If furnishing-specific comparison was used
        if result["comparison_type"] == "Furnishing-specific":

            # Breakdown should only show selected comparables
            breakdown = result["furnishing_breakdown"]
            breakdown_total = sum(breakdown.values())

            # Breakdown total must equal listing_count
            assert breakdown_total == result["listing_count"], (
                f"Breakdown total {breakdown_total} != listing_count {result['listing_count']}. "
                f"Breakdown: {breakdown}"
            )

            # For furnishing-specific, the target furnishing should dominate
            # (though mixed-furnishing fallback may have happened on different data)
            assert result["furnishing_listing_count"] >= 4

    def test_all_furnishing_fallback_breakdown_matches_selected(self):
        """
        When using all-furnishing fallback, breakdown should still match
        the actual selected comparables (all of them in this case).
        """
        # Use parameters that likely trigger fallback
        # (uncommon furnishing or small sample)
        result = get_furnishing_market_reference(
            target_locality="Marathahalli",
            target_bhk=4,
            target_size=2500,
            target_furnishing="Unfurnished",
            min_furnishing_comparables=4
        )

        # If we have comparables but not enough for furnishing-specific
        if result["listing_count"] > 0:

            breakdown = result["furnishing_breakdown"]
            breakdown_total = sum(breakdown.values())

            # Breakdown total must equal listing_count
            assert breakdown_total == result["listing_count"], (
                f"Breakdown total {breakdown_total} != listing_count {result['listing_count']}. "
                f"Breakdown: {breakdown}"
            )

    def test_breakdown_corresponds_to_selected_comparables_dataframe(self):
        """
        The furnishing breakdown should exactly match the returned comparables DataFrame.
        """
        result = get_furnishing_market_reference(
            target_locality="Koramangala",
            target_bhk=2,
            target_size=1000,
            target_furnishing="Furnished",
            min_furnishing_comparables=4
        )

        if result["listing_count"] > 0:

            # Calculate breakdown from returned comparables
            comparables_df = result["comparables"]
            actual_breakdown = (
                comparables_df["furnishing_status"]
                .replace("", "Unknown")
                .value_counts()
                .to_dict()
            )

            # Should match exactly
            assert result["furnishing_breakdown"] == actual_breakdown, (
                f"Reported breakdown {result['furnishing_breakdown']} "
                f"!= actual comparables breakdown {actual_breakdown}"
            )

    def test_whitefield_semi_furnished_specific_case(self):
        """
        Specific regression test for the reported Whitefield case.

        Manual Test B:
        - Whitefield, 2 BHK, 1200 sq.ft., Semi-Furnished
        - Previously showed: 5 comparables used, but breakdown totaled 7

        After fix, breakdown should total exactly 5.
        """
        result = get_furnishing_market_reference(
            target_locality="Whitefield",
            target_bhk=2,
            target_size=1200,
            target_furnishing="Semi-Furnished",
            min_furnishing_comparables=4
        )

        if result["listing_count"] > 0:

            listing_count = result["listing_count"]
            breakdown = result["furnishing_breakdown"]
            breakdown_total = sum(breakdown.values())

            # Core fix verification
            assert breakdown_total == listing_count, (
                f"Whitefield Semi-Furnished case: "
                f"breakdown total {breakdown_total} != listing_count {listing_count}. "
                f"Breakdown: {breakdown}, "
                f"Comparison type: {result['comparison_type']}"
            )


class TestExistingFunctionalityPreserved:
    """Ensure fixes don't break existing behavior."""

    def test_furnishing_specific_still_works(self):
        """Furnishing-specific comparison should still activate when appropriate."""
        result = get_furnishing_market_reference(
            target_locality="HSR Layout",
            target_bhk=2,
            target_size=1100,
            target_furnishing="Semi-Furnished",
            min_furnishing_comparables=4
        )

        # Should find comparables in HSR Layout
        if result["listing_count"] >= 4:
            # If enough semi-furnished exist, should use furnishing-specific
            if result["furnishing_listing_count"] >= 4:
                assert result["comparison_type"] == "Furnishing-specific"

    def test_all_furnishing_fallback_still_works(self):
        """All-furnishing fallback should still work."""
        result = get_furnishing_market_reference(
            target_locality="Marathahalli",
            target_bhk=4,
            target_size=2800,
            target_furnishing="Furnished",
            min_furnishing_comparables=10  # High threshold to force fallback
        )

        # If we have general comparables but not enough furnishing-specific
        if result["listing_count"] > 0:
            if result["furnishing_listing_count"] < 10:
                assert result["comparison_type"] == "All-furnishing fallback"

    def test_ambiguous_availability_counting_logic(self):
        """Ambiguous availability count should reflect actual selected comparables."""
        result = get_furnishing_market_reference(
            target_locality="Indiranagar",
            target_bhk=2,
            target_size=1200,
            target_furnishing="Furnished",
            min_furnishing_comparables=4
        )

        if result["listing_count"] > 0:

            ambiguous_count = result["ambiguous_availability_count"]

            # Should be non-negative integer
            assert isinstance(ambiguous_count, int)
            assert ambiguous_count >= 0

            # Cannot exceed total listing count
            assert ambiguous_count <= result["listing_count"]


class TestAvailabilityStatusCounting:
    """Test that availability status counting handles edge cases correctly."""

    def test_nan_availability_status_counted_as_ambiguous(self):
        """NaN availability statuses should be counted as ambiguous."""
        # Create a minimal test DataFrame with NaN availability
        test_df = pd.DataFrame({
            "target_locality": ["TestLocality"] * 3,
            "bhk": [2, 2, 2],
            "size_sqft": [1000, 1050, 1100],
            "rent": [20000, 21000, 22000],
            "furnishing_status": ["Furnished", "Furnished", "Furnished"],
            "availabilityStatus": [pd.NA, "Ready to Move", "Inc Info"],
            "fetched_at": [None, None, None]
        })

        # Save and load to simulate real CSV behavior
        import tempfile
        import os
        from pathlib import Path

        # Get the project root and ensure processed directory exists
        PROJECT_ROOT = Path(__file__).resolve().parents[1]
        processed_dir = PROJECT_ROOT / "data" / "processed"

        # Backup original file if it exists
        input_file = processed_dir / "all_live_clean_standardized.csv"
        backup_file = processed_dir / "all_live_clean_standardized.csv.test_backup"

        original_exists = input_file.exists()
        if original_exists:
            import shutil
            shutil.copy(input_file, backup_file)

        try:
            # Write test data
            test_df.to_csv(input_file, index=False)

            # Test the function
            result = get_furnishing_market_reference(
                target_locality="TestLocality",
                target_bhk=2,
                target_size=1050,
                target_furnishing="Furnished",
                min_furnishing_comparables=2
            )

            # Should find all 3 records
            assert result["listing_count"] == 3

            # Should count NaN and "Inc Info" as ambiguous (2 out of 3)
            assert result["ambiguous_availability_count"] == 2

        finally:
            # Restore original file
            if original_exists:
                shutil.move(backup_file, input_file)
            elif input_file.exists():
                os.remove(input_file)

    def test_whitespace_only_status_counted_as_ambiguous(self):
        """Whitespace-only availability statuses should be counted as ambiguous."""
        test_df = pd.DataFrame({
            "target_locality": ["TestLocality2"] * 4,
            "bhk": [2, 2, 2, 2],
            "size_sqft": [1000, 1050, 1100, 1150],
            "rent": [20000, 21000, 22000, 23000],
            "furnishing_status": ["Furnished"] * 4,
            "availabilityStatus": ["  ", "", "Ready to Move", "   \t  "],
            "fetched_at": [None] * 4
        })

        from pathlib import Path
        PROJECT_ROOT = Path(__file__).resolve().parents[1]
        input_file = PROJECT_ROOT / "data" / "processed" / "all_live_clean_standardized.csv"
        backup_file = PROJECT_ROOT / "data" / "processed" / "all_live_clean_standardized.csv.test_backup"

        original_exists = input_file.exists()
        if original_exists:
            import shutil
            shutil.copy(input_file, backup_file)

        try:
            test_df.to_csv(input_file, index=False)

            result = get_furnishing_market_reference(
                target_locality="TestLocality2",
                target_bhk=2,
                target_size=1050,
                target_furnishing="Furnished",
                min_furnishing_comparables=2
            )

            assert result["listing_count"] == 4

            # All whitespace variants and empty string should be ambiguous (3 out of 4)
            assert result["ambiguous_availability_count"] == 3

        finally:
            if original_exists:
                import shutil
                shutil.move(backup_file, input_file)
            elif input_file.exists():
                import os
                os.remove(input_file)

    def test_recognized_ambiguous_labels_counted(self):
        """Recognized ambiguous labels like 'Inc Info', 'Already Listed' should be counted."""
        test_df = pd.DataFrame({
            "target_locality": ["TestLocality3"] * 5,
            "bhk": [2] * 5,
            "size_sqft": [1000, 1050, 1100, 1150, 1200],
            "rent": [20000, 21000, 22000, 23000, 24000],
            "furnishing_status": ["Furnished"] * 5,
            "availabilityStatus": [
                "Inc Info",
                "Already Listed",
                "Unknown",
                "Ready to Move",
                "INC INFO"  # Case insensitive
            ],
            "fetched_at": [None] * 5
        })

        from pathlib import Path
        PROJECT_ROOT = Path(__file__).resolve().parents[1]
        input_file = PROJECT_ROOT / "data" / "processed" / "all_live_clean_standardized.csv"
        backup_file = PROJECT_ROOT / "data" / "processed" / "all_live_clean_standardized.csv.test_backup"

        original_exists = input_file.exists()
        if original_exists:
            import shutil
            shutil.copy(input_file, backup_file)

        try:
            test_df.to_csv(input_file, index=False)

            result = get_furnishing_market_reference(
                target_locality="TestLocality3",
                target_bhk=2,
                target_size=1100,
                target_furnishing="Furnished",
                min_furnishing_comparables=2
            )

            assert result["listing_count"] == 5

            # "Inc Info", "Already Listed", "Unknown", "INC INFO" = 4 ambiguous
            assert result["ambiguous_availability_count"] == 4

        finally:
            if original_exists:
                import shutil
                shutil.move(backup_file, input_file)
            elif input_file.exists():
                import os
                os.remove(input_file)

    def test_unavailable_statuses_excluded_not_double_counted(self):
        """Records marked 'Rented' or 'Timed Out' should be excluded, not counted as ambiguous."""
        test_df = pd.DataFrame({
            "target_locality": ["TestLocality4"] * 6,
            "bhk": [2] * 6,
            "size_sqft": [1000, 1050, 1100, 1150, 1200, 1250],
            "rent": [20000, 21000, 22000, 23000, 24000, 25000],
            "furnishing_status": ["Furnished"] * 6,
            "availabilityStatus": [
                "Rented Out",  # Should be excluded
                "Ready to Move",
                "Inc Info",  # Should be ambiguous
                "Timed Out",  # Should be excluded
                "",  # Should be ambiguous
                "Available"
            ],
            "fetched_at": [None] * 6
        })

        from pathlib import Path
        PROJECT_ROOT = Path(__file__).resolve().parents[1]
        input_file = PROJECT_ROOT / "data" / "processed" / "all_live_clean_standardized.csv"
        backup_file = PROJECT_ROOT / "data" / "processed" / "all_live_clean_standardized.csv.test_backup"

        original_exists = input_file.exists()
        if original_exists:
            import shutil
            shutil.copy(input_file, backup_file)

        try:
            test_df.to_csv(input_file, index=False)

            result = get_furnishing_market_reference(
                target_locality="TestLocality4",
                target_bhk=2,
                target_size=1100,
                target_furnishing="Furnished",
                min_furnishing_comparables=2
            )

            # Should exclude "Rented Out" and "Timed Out", leaving 4 comparables
            assert result["listing_count"] == 4

            # Of the 4 remaining, "Inc Info" and "" are ambiguous = 2
            assert result["ambiguous_availability_count"] == 2

        finally:
            if original_exists:
                import shutil
                shutil.move(backup_file, input_file)
            elif input_file.exists():
                import os
                os.remove(input_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
