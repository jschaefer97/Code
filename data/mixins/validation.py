import inspect
from loguru import logger

class ValidationMixin:
    def _validate_df(self, df, expected_value, attr_key):
        """
        Strictly validates that the DataFrame has a specific `.attrs` attribute set to the expected value.

        Parameters:
            df (pd.DataFrame): The DataFrame to validate.
            attr_key (str): The key in df.attrs to check.
            expected_value (Any): The expected value for that attribute.

        Raises:
            ValueError: If the attribute is missing or has an unexpected value.
        """
        # Get the name of the caller function (one frame up)
        caller = inspect.stack()[1].function
        actual_value = df.attrs.get(attr_key, None)

        if actual_value != expected_value:
            raise ValueError(
                f"{self.name}.{caller}: Validation failed for dataset: expected "
                f"attrs['{attr_key}'] = '{expected_value}', but found '{actual_value}'."
            )

        logger.info(
            f"{self.name}.{caller}: Dataset passed validation: attrs['{attr_key}'] = '{expected_value}'."
        )
