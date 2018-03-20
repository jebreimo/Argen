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
        self.properties = properties.copy()
        self.type = None
        self.default = None
        self.member_action = None
        self.member_callback = None
