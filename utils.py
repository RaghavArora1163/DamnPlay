def standardize_response(success, data=None, message=None):
    """
    Utility function to standardize API responses.

    Args:
        success (bool): Indicates if the request was successful.
        data (any): The response data (must be JSON serializable).
        message (str): Optional message to include in the response.

    Returns:
        dict: A standardized response structure.
    """
    return {
        "success": success,
        "data": data if data is not None else {},
        "message": message if message else ("Success" if success else "An error occurred")
    }
