"""Welcome to Reflex! This file showcases the custom component in a basic app."""

import logging
import os
from textwrap import dedent

import reflex as rx
import reflex_clerk_api as clerk
from dotenv import load_dotenv
from reflex.event import EventType
from rxconfig import config

# Set up debug logging with a console handler
logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler()])
logging.debug("Logging is set up.")


load_dotenv()

filename = f"{config.app_name}/{config.app_name}.py"


class State(rx.State):
    """The app state."""

    # Store information that is populated during an on_load event.
    info_from_load: str = "Not loaded yet."
    # Store information whenever the user logs in or out.
    last_auth_change: str = "No changes yet."

    @rx.event
    async def do_something_on_load(self) -> EventType:
        """Example of a handler that should run on_load, but *after* the ClerkState is updated.

        E.g., The handler needs to know whether the user is logged in or not.
        """
        clerk_state = await self.get_state(clerk.ClerkState)
        self.info_from_load = f"""\
        State.is_hydrated: {self.is_hydrated}
        clerkstate.auth_checked: {clerk_state.auth_checked}
        ClerkState.is_logged_in: {clerk_state.is_signed_in}
        """
        return rx.toast.info("On load event has finished")

    @rx.event
    async def do_something_on_log_in_or_out(self) -> EventType:
        """Demo handler that should run on user login or logout.

        To make this run it is registered via
        `clerk.register_on_auth_change_handler(State.do_something_on_log_in_or_out)`
        """
        clerk_state = await self.get_state(clerk.ClerkState)
        if clerk_state.is_signed_in:
            self.last_auth_change = "User signed in"
            return rx.toast.success("User just signed in!", position="top-center")
        else:
            self.last_auth_change = "User signed out"
            return rx.toast.warning("User just signed out!", position="top-center")


def demo_page_header_and_description() -> rx.Component:
    return rx.vstack(
        rx.heading("reflex-clerk-api demo", size="9"),
        rx.heading(
            "Custom",
            rx.link(rx.code("reflex"), href="https://reflex.dev"),
            "components that wrap Clerk react components (",
            rx.link(
                rx.code("@clerk/clerk-react"),
                href="https://www.npmjs.com/package/@clerk/clerk-react",
            ),
            ") and interact with the Clerk backend API.",
            size="4",
        ),
        rx.heading(
            "See the ",
            rx.link(
                "overview of Clerk components",
                href="https://clerk.com/docs/components/overview",
            ),
            " for more info on the wrapped components.",
            size="5",
        ),
        rx.divider(),
        rx.text(
            "Note: This is intended to be roughly a drop-in replacement of the ",
            rx.code("kroo/reflex-clerk"),
            " package that is no longer maintained.",
        ),
        rx.heading(
            "In addition to wrapping the basic components (and in comparison to Kroo's implementation), this additionally:",
            size="5",
        ),
        rx.unordered_list(
            rx.list_item(
                "uses Clerk's maintained python backend api (",
                rx.link(
                    "clerk-backend-api",
                    href="https://pypi.org/project/clerk-backend-api/",
                ),
                ")",
            ),
            rx.list_item(
                "is fully asynchronous, using ",
                rx.code("async/await"),
                " for all requests to the Clerk backend",
            ),
            rx.list_item("supports reflex 0.7.x"),
            rx.list_item(
                "adds a helper for handling ",
                rx.code("on_load"),
                " events that require knowledge of user authentication status. (i.e. ensuring the ClerkState is updated first)",
            ),
            rx.list_item(
                "adds a way to register event handlers that should be called on authentication changes (login/logout)"
            ),
        ),
    )


copy_button = rx.button(
    rx.icon("copy"),
    variant="soft",
    position="absolute",
    top="8px",
    right="0",
)


def getting_started() -> rx.Component:
    return rx.vstack(
        rx.heading("Getting Started", size="6"),
        rx.text("Install with pip: "),
        rx.code_block(
            "pip install reflex-clerk-api",
            language="bash",
            can_copy=True,
            copy_button=copy_button,
        ),
        rx.text("Or with a package manager (uv/poetry):"),
        rx.code_block(
            "uv add reflex-clerk-api",
            language="bash",
            can_copy=True,
            copy_button=copy_button,
        ),
        rx.heading(
            "Import the package",
            size="5",
        ),
        rx.code_block(
            "import reflex_clerk_api as clerk",
            language="python",
            can_copy=True,
            copy_button=copy_button,
        ),
        rx.accordion.root(
            rx.accordion.item(
                header="Minimal example",
                content=rx.code_block(
                    dedent("""\
                import reflex_clerk_api as clerk

                def index() -> rx.Component:
                    return clerk.clerk_provider(
                        clerk.clerk_loaded(
                            clerk.signed_in(
                                clerk.sign_on(
                                    rx.button("Sign out"),
                                ),
                            ),
                            clerk.signed_out(
                                rx.button("Sign in"),
                            ),
                        ),
                        publishable_key=os.environ["CLERK_PUBLISHABLE_KEY"],
                        secret_key=os.environ["CLERK_SECRET_KEY"],
                        register_user_state=True,
                    )
                """),
                    language="python",
                ),
            ),
            collapsible=True,
            variant="soft",
        ),
    )


def migration_notes() -> rx.Component:
    return rx.vstack(
        rx.text("Migration notes:"),
        rx.unordered_list(
            rx.list_item(
                "update your import to be from `reflex_clerk_api` instead of `reflex_clerk`"
            ),
            rx.list_item(
                rx.markdown(
                    "use `clerk.add_sign_in_page(...)` and `clerk.add_sign_up_page(...)` instead of `clerk.install_pages(...)`"
                )
            ),
            rx.list_item(
                rx.markdown(
                    "wrap `on_load` events with `clerk.on_load(<on_load_events>)` to ensure the ClerkState is updated before other on_load events (i.e. is_signed_in will be accurate)"
                )
            ),
            rx.list_item(
                rx.markdown(
                    "use `await clerk.get_user()` inside event handlers instead of `clerk_state.user` to explicitly retrieve user information when desired"
                )
            ),
            rx.list_item(
                "Note that you can use the `clerk_backend_api` directly if desired (it is a dependency of this plugin anyway)"
            ),
        ),
    )


def demo_card(
    heading: str, description: str | rx.Component, demo: rx.Component
) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading(heading, size="5"),
            rx.text(description) if isinstance(description, str) else description,
            rx.divider(),
            demo,
        ),
        max_width="30em",
    )


def current_clerk_state_values() -> rx.Component:
    demo = rx.vstack(
        rx.text(
            f"""State.is_hydrated: {State.is_hydrated},
                ClerkState.auth_checked: {clerk.ClerkState.auth_checked},
                ClerkState.is_logged_in: {clerk.ClerkState.is_signed_in}""",
            white_space="pre-line",
            margin_top="1em",
        ),
    )
    return demo_card(
        "Current ClerkState values",
        "Showing the current state of the ClerkState variables.",
        demo,
    )


def on_load_demo() -> rx.Component:
    demo = rx.card(
        rx.text("What the state saw during it's on_load event:"),
        rx.text(
            State.info_from_load,
            read_only=True,
            white_space="pre-line",
            margin_top="1em",
        ),
    )
    return demo_card(
        "Better on_load handling",
        rx.markdown(
            dedent("""\
            By using setting `on_load=clerk.on_load([...])`,
            you can ensure that the `ClerkState` is updated before any other `on_load` events are run.

            This is necessary because the ClerkState authentication is triggered from a frontend event that
            can't be guaranteed to run before the other `on_load` events.
            """)
        ),
        demo,
    )


def on_auth_change_demo() -> rx.Component:
    return demo_card(
        "On auth change callbacks",
        rx.vstack(
            rx.text(
                "You can register a method to be called when the user logs in or out."
            ),
            rx.markdown(
                dedent("""\
                ```python
                clerk.register_on_auth_change_handler(State.do_something_on_log_in_or_out)
                ```"""),
                wrap_long_lines=True,
                width="100%",
            ),
            width="100%",
        ),
        rx.vstack(
            rx.text(
                "In this demo, you'll see a toast top-center when you log in or out as well as the state variable change below."
            ),
            rx.text(f"State.last_auth_change={State.last_auth_change}"),
        ),
    )


def clerk_loaded_demo() -> rx.Component:
    signed_in_area = rx.card(
        rx.vstack(
            rx.text("You'll only see content below if you are signed in"),
            clerk.signed_in(
                "You are signed in.",
                clerk.sign_out_button(rx.button("Sign out")),
            ),
        )
    )
    signed_out_area = rx.card(
        rx.vstack(
            rx.text("You'll only see content below if you are signed out"),
            clerk.signed_out(
                "You are signed out.",
                clerk.sign_in_button(rx.button("Sign in")),
            ),
        )
    )

    demo = rx.fragment(
        clerk.clerk_loading(
            rx.text("Clerk is loading..."),
            rx.spinner(size="3"),
        ),
        clerk.clerk_loaded(
            rx.vstack(
                rx.text("Clerk is loaded!"),
                rx.grid(
                    signed_in_area,
                    signed_out_area,
                    columns="2",
                    spacing="3",
                ),
                align="center",
            ),
        ),
    )
    return demo_card(
        "Clerk loaded and signed in/out areas",
        rx.markdown(
            "Demo of `clerk_loaded`, `clerk_loading`, and `signed_in`, `signed_out` components."
        ),
        demo,
    )


def links_to_demo_pages() -> rx.Component:
    demo = rx.fragment(
        clerk.signed_out(
            rx.grid(
                rx.link(rx.button("Go to sign up page", width="100%"), href="/sign-up"),
                rx.link(rx.button("Go to sign in page", width="100%"), href="/sign-in"),
                width="100%",
                columns="2",
                spacing="3",
            )
        ),
        clerk.signed_in(
            rx.text("Sign out to see links to default sign-in and sign-up pages.")
        ),
    )
    return demo_card(
        "Default sign-in and sign-up pages",
        rx.markdown(
            dedent("""\
            These are some built-in sign-in and sign-up pages. To use them, just do:

            ```python
            clerk.add_sign_in_page(app)
            clerk.add_sign_up_page(app)
            ```

            You can also create your own with more customization.""")
        ),
        demo,
    )


def user_info_demo() -> rx.Component:
    def item(label: str, value: rx.Component | str) -> rx.Component:
        return rx.data_list.item(
            rx.data_list.label(label),
            rx.data_list.value(value),
        )

    demo = rx.vstack(
        clerk.signed_in(
            rx.hstack(
                rx.card(
                    rx.data_list.root(
                        item("first name", clerk.ClerkUser.first_name),
                        item("last name", clerk.ClerkUser.last_name),
                        item("username", clerk.ClerkUser.username),
                        item("email", clerk.ClerkUser.email_address),
                        item("has image", rx.text(clerk.ClerkUser.has_image)),
                    ),
                    # border=f"1px solid {rx.color('gray', 6)}",
                    # padding="2em",
                ),
                rx.avatar(src=clerk.ClerkUser.image_url, fallback="No image", size="9"),
                width="100%",
                justify="center",
                spacing="5",
            )
        ),
        rx.divider(),
        clerk.signed_out(rx.text("Sign in to see user information.")),
    )

    return demo_card(
        "Built-in User info",
        rx.markdown(
            dedent("""\
            To conveniently use basic information within the frontend, you can use the `clerk.ClerkUser` state.[^1]

            Full user information can also be retrieved within event handler methods via `await clerk.get_user(self)`.

            [^1]: *Enable this behvior with:*
            ```clerk.clerk_provider(..., register_user_state=True)```
            """)
        ),
        demo,
    )


def index() -> rx.Component:
    clerk.register_on_auth_change_handler(State.do_something_on_log_in_or_out)

    return clerk.clerk_provider(
        rx.container(
            rx.vstack(
                demo_page_header_and_description(),
                rx.divider(),
                rx.hstack(
                    getting_started(),
                    migration_notes(),
                ),
                rx.button("Dev reset", on_click=clerk.ClerkState.dev_reset),
                rx.divider(),
                rx.grid(
                    current_clerk_state_values(),
                    clerk_loaded_demo(),
                    on_load_demo(),
                    on_auth_change_demo(),
                    user_info_demo(),
                    links_to_demo_pages(),
                    columns=rx.breakpoints(initial="1", sm="2"),
                    spacing="4",
                ),
                align="center",
                spacing="7",
            ),
            height="100vh",
            size="4",
            overflow_y="auto",
        ),
        publishable_key=os.environ["CLERK_PUBLISHABLE_KEY"],
        register_user_state=True,
        secret_key=os.environ.get("CLERK_SECRET_KEY"),
    )


# Add state and page to the app.
app = rx.App()
# NOTE: Use the `clerk.on_load` to ensure that the ClerkState is updated *before* any other on_load events are run.
#  The `ClerkState` is updated by an event sent from the frontend that is not guaranteed to run before the reflex on_load events.
app.add_page(index, on_load=clerk.on_load([State.do_something_on_load]))
clerk.add_sign_in_page(app)
clerk.add_sign_up_page(app)
