#!/bin/bash

# Author: Tibor Dudlák

. /usr/share/beakerlib/beakerlib.sh || ( echo "FAILED to source beakerlib" && exit 1 )

install_package () {
    rlPhaseStartSetup "Installing $1"
        rlRun "dnf install -y $1"
    rlPhaseEnd
}

print_and_remove_mrack_log(){
    rlPhaseStartTest "Print and remove mrack.log"
        rlRun "cat mrack.log && rm -f mrack.log"
    rlPhaseEnd
}

rm_mracklog_run_mrack_up () {
    rlPhaseStartTest "Remove mrack.log and run mrack up"
        rlRun "rm -f mrack.log"
        rlRun "mrack up 2>&1 | grep 'Installed providers:'"
    rlPhaseEnd
}

rlJournalStart
    rlPhaseStartSetup "Check required packages and absence of mrack"
        rlAssertRpm "which"
        rlRun "dnf remove -y `rpm -qa | grep mrack` || true"
    rlPhaseEnd

    rlPhaseStartTest "mrack should not be pre-installed on system"
        rlRun "python3 -c \"import mrack\"" 1
    rlPhaseEnd

    install_package "python3-mracklib"

    rlPhaseStartTest "mrack command NOT present on system"
        rlRun "which mrack 2>&1 | grep -i 'no' | grep 'mrack'"
    rlPhaseEnd

    install_package "mrack-cli"

    rlPhaseStartTest "mrack command present on system"
        rlRun "which mrack | grep 'bin/mrack'"
        rlRun "mrack --version"
    rlPhaseEnd

    install_package "python3-mrack-beaker"

    rm_mracklog_run_mrack_up

    install_package "mrack"

    rm_mracklog_run_mrack_up

    print_and_remove_mrack_log

    rlPhaseStartSetup "Reinstall mrack"
        rlRun "dnf reinstall mrack -y"
    rlPhaseEnd

    rm_mracklog_run_mrack_up

    print_and_remove_mrack_log

rlJournalEnd
