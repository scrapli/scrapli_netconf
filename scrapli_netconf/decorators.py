"""scrapli_netconf.decorators"""
from functools import update_wrapper
from typing import Any, Callable
from warnings import warn


class DeprecateFilters:  # pragma: no cover
    warning = (
        "`filters` has been renamed `filter_` for consistency with `get` and `rpc` methods,  and "
        "no longer supports a list of strings. Please  pass a string payload here. `filters` will "
        "be deprecated in future releases!"
    )

    def __call__(self, wrapped_func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Decorate get_config `filters` argument

        Deprecate the `filters` argument in favor of `filter_` for better consistency in function
        signatures for `get`, `get_config`, and `rpc`

        Args:
            wrapped_func: function being decorated

        Returns:
            decorate: decorated func

        Raises:
            N/A

        """

        def decorate(*args: Any, **kwargs: Any) -> Any:
            filters = kwargs.pop("filters", None)

            if filters is None:
                return wrapped_func(*args, **kwargs)

            warn(self.warning, FutureWarning)

            if isinstance(filters, list):
                filter_ = "".join(filters)
            elif isinstance(filters, str):
                filter_ = filters
            else:
                raise Exception

            return wrapped_func(*args, filter_=filter_, **kwargs)

        # ensures that the wrapped function is updated w/ the original functions docs/etc. --
        # necessary for introspection for the auto gen docs to work!
        update_wrapper(wrapper=decorate, wrapped=wrapped_func)
        return decorate
