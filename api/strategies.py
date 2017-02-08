from hypothesis.strategies import (
    builds,
    lists,
    one_of,
    text,
)

from string import (
    ascii_letters,
    digits,
    printable,
)


# Usernames as expected by the Django User model:
usernames = text(
    min_size=1,
    max_size=150,
    alphabet=ascii_letters + digits + '@.+-_',
)


# Nonempty passwords restricted to printable ASCII characters to avoid issues
# with HTTP Basic authentication credential encoding:
passwords = (
    text(
        min_size=1,
        alphabet=printable,
    )
    .map(str.strip).filter(lambda x: x)  # Python strips password strings!
)


# Domain name labels, each of the dot-separated components of a domain name:
def domain_labels(min_size=1):
    return (
        text(
            alphabet=ascii_letters + digits + '-',
            min_size=min_size,
            max_size=63,
        )
        .filter(
            lambda label:
                # Domain name labels must not start or end with a dash:
                label[0] != '-' and label[-1] != '-'
        )
    )


# Domain names:
domains = (
    builds(
        # Domain names are generated in two parts to satisfy Django's validator:
        # all domain labels except the last one, and then the final, top-level
        # domain label.  The Django domain name validator requires the top-level
        # label to have at least two characters, while the rest may have only a
        # single character, so this is necessary to match the validator.
        lambda start, end: (
            start + [end]
        ),

        # There must be at least one dot in the domain name, so this generates
        # at least one label before the final one:
        lists(
            domain_labels(),
            min_size=1,
        ),

        # The last domain label must not be a single character:
        domain_labels(
            min_size=2,
        ),
    )
    .map('.'.join)
)


# The first part of an e-mail address, before the @:
email_local_parts = text(
    alphabet=ascii_letters + digits + "-!#$%&'*+/=?^_`{}|~",
    min_size=1,
    max_size=252,
).filter(lambda username: len(username) < 252)


# E-mail addresses as expected by the Django e-mail address model field:
emails = builds(
    lambda user, domain: f'{user}@{domain}',
    one_of(
        email_local_parts,
        builds(
            lambda username, tag: (
                f'{username}+{tag}'
            ),
            email_local_parts,
            email_local_parts,
        ),
    ),
    domains,
).filter(lambda email: len(email) < 254)
