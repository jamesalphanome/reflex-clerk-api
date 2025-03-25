import os
import uuid
from pathlib import Path
from typing import Iterator

import clerk_backend_api
import pytest
from clerk_backend_api import Clerk
from dotenv import load_dotenv
from playwright.sync_api import Page, expect
from reflex.testing import AppHarness

load_dotenv()

TEST_EMAIL = "ci-test+clerk_test@gmail.com"
TEST_PASSWORD = "test-clerk-password"


@pytest.fixture(scope="session")
def demo_app():
    app_root = Path(__file__).parent.parent / "clerk_api_demo"
    with AppHarness.create(root=app_root) as harness:
        yield harness


@pytest.fixture(scope="function")
def page(
    request: pytest.FixtureRequest, demo_app: AppHarness, page: Page
) -> Iterator[Page]:
    """Load the demo app main page."""
    page.set_default_timeout(10000)
    assert demo_app.frontend_url is not None
    page.goto(demo_app.frontend_url)
    page.set_default_timeout(2000)
    yield page
    if request.session.testsfailed:
        print("Test failed. Saving screenshot as playwright_test_error.png")
        page.screenshot(path="playwright_test_error.png")


@pytest.fixture()
def clerk_client() -> Iterator[Clerk]:
    """Create clerk backend api client."""
    secret_key = os.environ["CLERK_SECRET_KEY"]
    with clerk_backend_api.Clerk(bearer_auth=secret_key) as client:
        yield client


@pytest.fixture
def create_test_user(clerk_client: Clerk) -> clerk_backend_api.models.User:
    """Creates (or checks already exists) a test clerk user.

    This can then be used to sign in during tests.
    """
    existing = clerk_client.users.list(request={"email_address": [TEST_EMAIL]})
    if existing is not None and len(existing) > 0:
        if len(existing) != 1:
            raise SetupError(
                "Multiple test users found with same email... This should not happen."
            )
        print("Test user already exists.")
        return existing[0]

    print("Creating test user...")
    res = clerk_client.users.create(
        request={
            "external_id": "ext-id-" + uuid.uuid4().hex[:5],
            "first_name": "John",
            "last_name": "Doe",
            "email_address": [
                TEST_EMAIL,
            ],
            "username": "fake_username_" + uuid.uuid4().hex[:5],
            "password": TEST_PASSWORD,
            "skip_password_checks": False,
            "skip_password_requirement": False,
            "public_metadata": {
                "role": "user",
            },
            "private_metadata": {
                "internal_id": "789",
            },
            "unsafe_metadata": {
                "preferences": {
                    "theme": "dark",
                },
            },
            "delete_self_enabled": True,
            "skip_legal_checks": False,
            "create_organization_enabled": True,
            "create_organizations_limit": 134365,
            "created_at": "2023-03-15T07:15:20.902Z",
        }
    )
    assert res is not None
    return res


def test_test_user(create_test_user: clerk_backend_api.models.User):
    """Check the test user was either created or found correctly."""
    user = create_test_user
    assert user.email_addresses is not None
    assert user.email_addresses[0].email_address == TEST_EMAIL


def test_render(page: Page):
    """Check that the demo renders correctly.

    I.e. Check components are visible.
    """
    expect(page.locator('[id="__next"]')).to_contain_text("reflex-clerk-api demo")
    expect(page.locator('[id="__next"]')).to_contain_text("Getting Started")
    expect(page.locator('[id="__next"]')).to_contain_text("Demos")
    expect(page.locator('[id="__next"]')).to_contain_text(
        "ClerkState variables and methods"
    )
    expect(page.locator('[id="__next"]')).to_contain_text(
        "Clerk loaded and signed in/out areas"
    )
    expect(page.locator('[id="__next"]')).to_contain_text("Better on_load handling")
    expect(page.locator('[id="__next"]')).to_contain_text("On auth change callbacks")
    expect(page.locator('[id="__next"]')).to_contain_text("ClerkUser info")
    expect(page.locator('[id="__next"]')).to_contain_text("Sign-in and sign-up pages")
    expect(page.locator('[id="__next"]')).to_contain_text("User rofile management")


def test_sign_up(page: Page):
    """Check sign-up button takes you to a sign-up form.

    Note: Can't actually test signing up in headless mode because of bot detection.
    """
    page.pause()
    page.get_by_role("button", name="Sign up").click()
    expect(page.get_by_role("heading")).to_contain_text("Create your account")


class SetupError(Exception):
    """Error raised when the test setup is incorrect."""


def test_sign_in(page: Page):
    """Check sign-in button takes you to a sign-in form.

    Note: Can't actually test signing in in headless mode because of bot detection.
    """

    page.get_by_role("button", name="Sign in").click()
    expect(page.get_by_role("heading")).to_contain_text("Sign in to")
    page.get_by_role("textbox", name="Email address").click()
    page.get_by_role("textbox", name="Email address").fill(TEST_EMAIL)
    page.get_by_role("button", name="Continue").click()
    page.get_by_role("textbox", name="Password").click()
    page.get_by_role("textbox", name="Password").fill(TEST_PASSWORD)
    page.get_by_role("button", name="Continue").click()
    expect(page.locator('[id="__next"]')).to_contain_text("Sign out")

    page.pause()
