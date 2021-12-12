from typing import ByteString
import flask
import pytest
import server


TEST_USERNAME = "testname"
TEMPLATES = ["templates/homepage.html", "templates/top-melons.html"]


@pytest.fixture
def client():
    server.app.config["TESTING"] = True

    with server.app.test_client() as client:
        yield client


@pytest.fixture
def client_with_name_in_session():
    """Fixture that provides a client that has a user's name stored in the session."""

    # We need to modify the session, *BUT* since we never specify the value of # the key used to store a user's name in the instructions, we have to do
    # this intermediary step to find the right key to use.
    #
    # First, we use test_client as a context manager so we can access
    # the session object. Then, we'll make a request to /get-name,
    # and search session for the key associated with our name
    # (which is just "testname")
    with server.app.test_client() as client:
        resp = client.get(f"/get-name?name={TEST_USERNAME}")
        if resp.status_code == 405:
            client.post(f"/get-name", data={"name": TEST_USERNAME})

        name_key, _ = search_for_value_in_session(flask.session, TEST_USERNAME)

    # Open another context, now that we know which session key to modify.
    with server.app.test_client() as client:
        with client.session_transaction() as sess:
            if name_key:
                sess[name_key] = TEST_USERNAME

        yield client


def search_for_value_in_session(flask_session, target_value):
    """Search flask_session for value and return its key and value if found."""

    for key, val in flask_session.items():
        if val == target_value:
            return key, val

    return None, None


def test_top_melons_renders_template_with_top_melons(
    client, client_with_name_in_session
):
    """/top-melons should show MOST_LOVED_MELONS on the Top Melons page."""

    response = client.get("/top-melons", follow_redirects=True)

    if b'<form action="/get-name"' in response.data:
        # If we're redirected to the homepage, it's probably because
        # the user's name isn't in the session yet, so instead, we should
        # make request using the client that has user's name in session.
        response = client_with_name_in_session.get(
            "/top-melons", follow_redirects=True
        )

    for melon_info in server.MOST_LOVED_MELONS.values():
        assert str.encode(melon_info["img"]) in response.data
        assert str.encode(melon_info["name"]) in response.data
        assert str.encode(str(melon_info["num_loves"])) in response.data


def test_render_homepage(client):
    """/ should render the homepage."""

    response = client.get("/")

    assert b"Ubermelon's Most Loved Melons" in response.data
    assert b"What's your name?" in response.data


def test_homepage_has_img(client):
    """/ should show an image."""

    response = client.get("/")

    assert b'src="#"' not in response.data


def test_get_name_stores_username_in_session(client):
    """/get-name should get user's name from form and store the name in session"""

    response = client.get(f"/get-name?name={TEST_USERNAME}")

    # If we get a 405, try using a POST request instead
    if response.status_code == 405:
        client.post("/get-name", data={"name": TEST_USERNAME})

    _, name_val = search_for_value_in_session(flask.session, TEST_USERNAME)

    assert name_val == TEST_USERNAME


def test_get_name_redirects_to_top_melons(client):
    """/get-name redirects to /top-melons"""

    response = client.get(
        f"/get-name?name={TEST_USERNAME}", follow_redirects=True
    )
    if response.status_code == 405:
        response = client.post(
            "/get-name", data={"name": TEST_USERNAME}, follow_redirects=True
        )

    assert b"Loved" in response.data
    assert b"melon-div" in response.data


def test_top_melons_displays_users_name(client_with_name_in_session):
    """/top-melons should display user's name in heading if a name is in the session."""

    response = client_with_name_in_session.get("/top-melons")

    assert str.encode(TEST_USERNAME) in response.data


def test_top_melons_redirects_to_home_if_no_user_in_session(client):
    """/top-melons should redirect to homepage if user's name isn't in the session."""

    response = client.get("/top-melons", follow_redirects=True)

    assert b"Ubermelon's Most Loved Melons" in response.data
    assert b"What's your name?" in response.data


def test_homepage_redirects_to_top_melons_if_user_in_session(
    client_with_name_in_session,
):
    """/ should redirect to /top-melons if the user's name is in the session."""

    response = client_with_name_in_session.get("/", follow_redirects=True)

    assert b"Loved" in response.data
    assert b"melon-div" in response.data


def test_base_template_uses_jinja_block():
    """Test that templates/base.html contains a Jinja block."""

    with open("templates/base.html") as f:
        contents = f.read()

    assert "{% block" in contents


def test_all_templates_inherit_from_base():
    """Test that all templates inherit from templates/base.html."""

    for template in TEMPLATES:
        with open(template) as f:
            contents = f.read()

        assert "{% extends" in contents


def test_templates_inherit_doctype_and_head_from_base():
    """Test that templates inherit <!doctype html>, <head>, and <body> from base."""

    for template in TEMPLATES:
        with open(template) as f:
            contents = f.read()

            assert "doctype" not in contents or "DOCTYPE" not in contents
            assert "<head>" not in contents
            assert "</head>" not in contents
            assert "<body>" not in contents
            assert "</body>" not in contents
