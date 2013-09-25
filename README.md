CLAPGen
=======

Generates sophisticated command line argument parsers for C++ programs

* Count: either a single integer or two integers separated by two dots (i.e. min..max). The default for options is 0..1 and for arguments it's 1.
  If the maximum isn't 1 the type automatically becomes a list
  If the maximum is 0 there is no upper bound for how many values the option accepts.
* Default: the default value for the variable
        Delimiter: a single character (e.g. comma) used to separate values in
            a list
        DelimiterCount: 0..2 3..
        Flags
        Index
        Member: the name of the member variable
        Name: the name of the value that will be used in error messages and
            also the name of the member unless "member" is also specified
            (any characters in the name that are illegal in member names are
             replaced with underscores).
        OptionType: ignored if set, it's always deduced from other parameters
            Value
            Argument
            DelimitedValue
            DelimitedArgument
        Text: overide the auto-generated text for the argument or option
        Type:
            Help
            Info
            MultiValue
            Value
            List    values are stored in a vector
            Final   the option marks the end of all options, all remaining
                    arguments are treated as arguments even if they start with
                    a dash. POSIX-compliant program should make "--" the
                    final option. There won't be a members for final options in
                    the Arguments struct.
        # Text: overide the auto-generated text for the argument or option
        Value: the value that will be assigned (or appended) to the variable
            if the flag is given.
        Values: the legal values for the argument or option. The same set of
            legal values applies to all values when "type" is "list" or
            "multi-value".
        ValueType: this is the type of the values of the option or argument.
            clapgen doesn't enforce any restrictions on the types, however the generated code is unlikely to compile unless the type is among the bool, integer or floating point types, or std::string. If the type or typedef used isn't defined in <cstddef>, <cstdint> or <string>, it is necessary to customize the generated file. Strings must be of type "std::string", just "string" won't work.
            # int int8_t int16_t int32_t int64_t
            # unsigned uint8_t uint16_t uint32_t uint64_t
            # float double
            String
