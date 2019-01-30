from contty.caddyfile import Caddyfile


def test_automatic_block_writing():
    caddyfile = Caddyfile()
    caddyfile.add_automatic_block_config({
        "hostname": "test.net",
        "email": "te@test.net",
        "service": "someService",
        "port": "8080",
    })

    output = """
# CONTTY STARTBLOCK AUTOMATIC {"hostname": "test.net", "email": "te@test.net", "service": "someService", "port": "8080"}
https://test.net {
    header -Server
    proxy / someService:8080 {
        websocket
        transparent
    }
    tls te@test.net
}
# CONTTY ENDBLOCK
"""
    result = caddyfile.get_lines()
    assert result == [output]


def test_manual_block_writing():
    manual_data = [
        "This is caddy,",
        "but I'm not your daddy.",
        "Just parsing configs,",
        "before I see John Wicks.",
    ]
    result_data = [
        "\n# CONTTY STARTBLOCK MANUAL",
        "This is caddy,",
        "but I'm not your daddy.",
        "Just parsing configs,",
        "before I see John Wicks.",
        "# CONTTY ENDBLOCK\n",
    ]
    caddyfile = Caddyfile()
    caddyfile.add_manual_block(manual_data)
    result = caddyfile.get_lines()
    assert len(result) == len(result_data)
    for i in range(len(result)):
        assert result[i] == result_data[i]


def test_unmanaged_config_writing():
    manual_data = [
        "This is caddy,",
        "but I'm not your daddy.",
        "Just parsing configs,",
        "before I see John Wicks.",
    ]
    result_data = [
        "This is caddy,",
        "but I'm not your daddy.",
        "Just parsing configs,",
        "before I see John Wicks.",
    ]
    caddyfile = Caddyfile()
    for line in manual_data:
        caddyfile.unmanaged_config.append(line)
    result = caddyfile.get_lines()
    assert len(result) == len(result_data)
    for i in range(len(result)):
        assert result[i] == result_data[i]


def test_combined_writing():
    manual_block_1 = [
        "This is caddy,",
        "but I'm not your daddy.",
    ]
    manual_block_2 = [
        "Just parsing configs,",
        "before I see John Wicks.",
    ]
    automatic_block_1 = {
        "hostname": "test.net",
        "email": "te@test.net",
        "service": "someService",
        "port": "8080",
    }
    automatic_block_2 = {
        "hostname": "kek.org",
        "email": "kek@kek.org",
        "service": "unservice",
        "port": "67",
    }
    unmanaged_config = [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "Aliquam quis nibh ullamcorper, lacinia nibh non, porttitor eros.",
        "Aliquam faucibus dui dignissim interdum semper.",
    ]

    caddyfile = Caddyfile()
    caddyfile.add_automatic_block_config(automatic_block_1)
    caddyfile.add_manual_block(manual_block_2)
    caddyfile.add_automatic_block_config(automatic_block_2)
    caddyfile.add_manual_block(manual_block_1)
    for line in unmanaged_config:
        caddyfile.unmanaged_config.append(line)

    correct_result = """Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Aliquam quis nibh ullamcorper, lacinia nibh non, porttitor eros.
Aliquam faucibus dui dignissim interdum semper.

# CONTTY STARTBLOCK MANUAL
Just parsing configs,
before I see John Wicks.
# CONTTY ENDBLOCK


# CONTTY STARTBLOCK MANUAL
This is caddy,
but I'm not your daddy.
# CONTTY ENDBLOCK


# CONTTY STARTBLOCK AUTOMATIC {"hostname": "test.net", "email": "te@test.net", "service": "someService", "port": "8080"}
https://test.net {
    header -Server
    proxy / someService:8080 {
        websocket
        transparent
    }
    tls te@test.net
}
# CONTTY ENDBLOCK


# CONTTY STARTBLOCK AUTOMATIC {"hostname": "kek.org", "email": "kek@kek.org", "service": "unservice", "port": "67"}
https://kek.org {
    header -Server
    proxy / unservice:67 {
        websocket
        transparent
    }
    tls kek@kek.org
}
# CONTTY ENDBLOCK
"""
    result = "\n".join(caddyfile.get_lines())
    assert result == correct_result
