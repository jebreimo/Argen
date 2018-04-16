# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-01-27.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================


class Member:
    def __init__(self, name, properties):
        self.name = name
        self.arguments = []
        self.given_properties = properties
        # self.properties = properties.copy()
        self.type = properties.get("type")
        self.default = properties.get("default")
        self.member_action = properties.get("member_action")
        self.member_callback = properties.get("member_callback")

    def __str__(self):
        values = self.__dict__
        keys = [k for k in values.keys() if k != "arguments"]
        keys.sort()
        kvs = ("%s: %s" % (k, values[k]) for k in keys if values[k] is not None)
        return "%s\n    %s" % (self.name, "\n    ".join(kvs))
