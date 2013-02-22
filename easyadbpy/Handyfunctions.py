# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

class Handyfunctions:
    #HANDY FUNCTIONS

    def getselectionvalue(selection):
        model , select =  selection.get_selected()
        return model.get_value(select, 0)
