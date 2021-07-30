RPC_FILTER = """<get-zones-information><terse/></get-zones-information>"""

RPC_ELEMENTS = []

RPC_EXPECTED = """<rpc-reply xmlns:junos="http://xml.juniper.net/junos/17.3R2/junos" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
    <zones-information xmlns="http://xml.juniper.net/junos/17.3R2/junos-zones" junos:style="terse">
        <zones-security>
            <zones-security-zonename>trust</zones-security-zonename>
            <zones-security-send-reset>On</zones-security-send-reset>
            <zones-security-policy-configurable>Yes</zones-security-policy-configurable>
            <zones-security-interfaces-bound>0</zones-security-interfaces-bound>
            <zones-security-interfaces>
            </zones-security-interfaces>
        </zones-security>
        <zones-security>
            <zones-security-zonename>untrust</zones-security-zonename>
            <zones-security-send-reset>Off</zones-security-send-reset>
            <zones-security-policy-configurable>Yes</zones-security-policy-configurable>
            <zones-security-screen>untrust-screen</zones-security-screen>
            <zones-security-interfaces-bound>0</zones-security-interfaces-bound>
            <zones-security-interfaces>
            </zones-security-interfaces>
        </zones-security>
        <zones-security>
            <zones-security-zonename>junos-host</zones-security-zonename>
            <zones-security-send-reset>Off</zones-security-send-reset>
            <zones-security-policy-configurable>Yes</zones-security-policy-configurable>
            <zones-security-interfaces-bound>0</zones-security-interfaces-bound>
            <zones-security-interfaces>
            </zones-security-interfaces>
        </zones-security>
    </zones-information>
</rpc-reply>"""
