from pynostr.event import Event
from pynostr.relay_manager import RelayManager
from pynostr.key import PrivateKey
import time
SKIP_TAGS = []
def build_nostr_entry(entry):

    skip_tags = SKIP_TAGS
    skip_tags.append("blog")
    skip_tags.append("documentation")


    toot_str = ''

    if "blog" in entry['tags']:
        toot_str += "New #Blog: "
    elif "documentation" in entry['tags']:
        toot_str += "New #Documentation: "

    toot_str += f"{entry['title']}\n"


    toot_str += f"\n\n{entry['link']}\n\n"

    # Tags to hashtags
    if len(entry['tags']) > 0:
        for tag in entry['tags']:
            if tag in skip_tags:
                # Skip the tag
                continue
            toot_str += f'#{tag.replace(" ", "")} '

    return toot_str


def Post(entry, nostr_private_key):
    NOSTR_RELAYS=[
    "wss://relayable.org",
    "wss://relay.damus.io",
    "wss://nostr.easydns.ca",
    "wss://nostrrelay.com",
    "wss://relay.snort.social",
    "wss://relay.nsecbunker.com"    
    ]
    try:
        # Set up the relay connections
        nostr_relay = RelayManager()
        nostr_pk = PrivateKey.from_nsec(nostr_private_key)

        for relay in NOSTR_RELAYS:
            nostr_relay.add_relay(relay)

        # Allow time for connections to open
        time.sleep(1.25)

        # Create and sign the event
        out_str = build_nostr_entry(entry)
        event = Event(out_str)
        event.sign(nostr_pk.hex())

        # Publish into the relays
        nostr_relay.publish_event(event)
        nostr_relay.run_sync()
        return True
    except Exception as e:
        print(f"Submitting to Nostr failed: {e}")
        return False

# Example usage:
# nostr_private_key = "nsec1uw78865hpalvlxyhernkatzslu45vfj94rvdqpynsuqfuuerkmqs56c3ws"
# entry_data = {"title": "WHo will win the elections in pakistan?", "link": "", "tags": []}
# Post(entry_data, nostr_private_key)
