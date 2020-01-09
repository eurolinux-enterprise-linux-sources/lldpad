# https://fedoraproject.org/wiki/Packaging:Guidelines#Compiler_flags
%define _hardened_build 1

Name:               lldpad
Version:            0.9.46
Release:            10%{?dist}
Summary:            Intel LLDP Agent
Group:              System Environment/Daemons
License:            GPLv2
URL:                http://open-lldp.org/
Source0:            %{name}-%{version}.tar.gz
Source1:            %{name}.init
Patch0:             %{name}-%{version}-123-g48a5f38.patch
Patch1:             %{name}-0.9.46-Ignore-supplied-PG-configuration-if-PG-is-being-disabled.patch
Requires:           kernel >= 2.6.32
BuildRequires:      automake autoconf libtool
BuildRequires:      flex >= 2.5.33
BuildRequires:      kernel-headers >= 2.6.32
BuildRequires:      libconfig-devel >= 1.3.2
BuildRequires:      libnl3-devel
BuildRequires:      readline-devel
Requires:           %{name}-libs%{?_isa} = %{version}-%{release}
Requires:           readline
Requires(post):     chkconfig
Requires(preun):    chkconfig
Requires(preun):    initscripts
Requires(postun):   initscripts
Provides:           dcbd = %{version}-%{release}
Obsoletes:          dcbd < 0.9.26

%description
This package contains the Linux user space daemon and configuration tool for
Intel LLDP Agent with Enhanced Ethernet support for the Data Center.

%package            libs
Summary:            Libraries for communication with %{name}
Group:              Development/Libraries

%description        libs
This package contains libraries used for communicating with %{name}.

%package            devel
Summary:            Development files for %{name} libraries
Group:              Development/Libraries
Requires:           %{name}-libs%{?_isa} = %{version}-%{release}
Provides:           dcbd-devel = %{version}-%{release}
Obsoletes:          dcbd-devel < 0.9.26

%description devel
The %{name}-devel package contains header files for developing applications
that use %{name}.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%build
./bootstrap.sh
%configure --disable-static
# fix the hardened build flags
sed -i -e 's! \\\$compiler_flags !&\\\$CFLAGS \\\$LDFLAGS !' libtool
make %{?_smp_mflags}

%install
make install DESTDIR=%{buildroot}
mkdir -p %{buildroot}%{_sharedstatedir}/%{name}
mkdir -p %{buildroot}%{_initddir}
install -m755 %{SOURCE1} %{buildroot}%{_initddir}/lldpad
rm -rf %{buildroot}/etc/init.d
rm -f %{buildroot}%{_mandir}/man8/dcbd.8
rm -f %{buildroot}%{_libdir}/liblldp_clif.la
rm -f %{buildroot}/usr/lib/systemd/system/%{name}.service
rm -f %{buildroot}/usr/lib/systemd/system/%{name}.socket

%post
/sbin/chkconfig --add %{name}

%preun
if [ $1 = 0 ]; then
    /sbin/service %{name} stop > /dev/null 2>&1
    /sbin/chkconfig --del %{name}
fi

%postun
if [ "$1" -ge "1" ]; then
    /sbin/service %{name} condrestart > /dev/null  2>&1 || :
fi

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%post devel
## provide legacy support for apps that use the old dcbd interface.
if [ ! -e %{_includedir}/dcbd ]; then
    ln -T -s %{_includedir}/lldpad %{_includedir}/dcbd
fi
if [ ! -e %{_includedir}/dcbd/clif_cmds.h ]; then
    ln -T -s %{_includedir}/lldpad/lldp_dcbx_cmds.h %{_includedir}/dcbd/clif_cmds.h
fi

%preun devel
if [ -e %{_includedir}/dcbd/clif_cmds.h ]; then
    rm -f %{_includedir}/dcbd/clif_cmds.h
fi
if [ -e %{_includedir}/dcbd ]; then
    rm -f %{_includedir}/dcbd
fi

%files
%defattr(-,root,root,-)
%doc COPYING README ChangeLog
%{_sbindir}/*
%dir %{_sharedstatedir}/%{name}
%{_initddir}/%{name}
%{_sysconfdir}/bash_completion.d/*
%{_mandir}/man8/*

%files libs
%defattr(-,root,root,-)
%doc COPYING README
%{_libdir}/liblldp_clif.so.*

%files devel
%defattr(-,root,root,-)
%{_includedir}/*
%{_libdir}/pkgconfig/*.pc
%{_libdir}/liblldp_clif.so

%changelog
* Tue Jan 24 2017 Chris Leech <cleech@redhat.com> - 0.9.46-10
- 1376807 rebase to newer version from RHEL 7.1

* Fri Jun 27 2014 Chris Leech <cleech@redhat.com> - 0.9.46-3
- Fix IEEE mode DCBX (#1104272)

* Tue Oct 15 2013 Petr Šabata <contyk@redhat.com> - 0.9.46-2
- Support multiple virtual machines again (#1017270)

* Thu Jun 20 2013 Petr Šabata <contyk@redhat.com> - 0.9.46-1
- Update o 0.9.46 (#829816)

* Fri Nov 23 2012 Petr Šabata <contyk@redhat.com> - 0.9.45-7
- Correct changelog bug references, thanks to Petr Písař
- Add explicit libs subpackage dependency

* Thu Nov 22 2012 Petr Šabata <contyk@redhat.com> - 0.9.45-6
- Willing SUT retains PFC operational state from peer after peer
  stops transmitting TLV (#870578)
- Unable to query configured PFC priorities under IEEE DCBX (#870576)

* Mon Nov 05 2012 Petr Šabata <contyk@redhat.com> - 0.9.45-5
- Subpackage liblldp_clif as lldpad-libs (#869633)

* Wed Oct 24 2012 Petr Šabata <contyk@redhat.com> - 0.9.45-4
- The devel subpackage now properly requires the base package to avoid
  multilib conflicts (#869633)

* Mon Oct 15 2012 Petr Šabata <contyk@redhat.com> - 0.9.45-3
- Include support for 802.1Qbg over bonding

* Thu Aug 23 2012 Petr Šabata <contyk@redhat.com> - 0.9.45-2
- Fix various issues regarding the display of the Management Address TLV
  (#819938, 327ef662)

* Wed Aug 15 2012 Petr Šabata <contyk@redhat.com> - 0.9.45-1
- Update to 0.9.45 (#819938)

* Mon Jul 02 2012 Petr Šabata <contyk@redhat.com> - 0.9.43-20
- Fix a bug in DCBX causing a possible link flap (1d7fac6a, #829857)

* Mon Jun 04 2012 Petr Šabata <contyk@redhat.com> - 0.9.43-19
- Enable APP attributes by default (d556e7b6, #824188)

* Tue Apr 24 2012 Petr Šabata <contyk@redhat.com> - 0.9.43-18
- A minor fix of the previous patch, thanks to Petr Písař

* Mon Apr 23 2012 Petr Šabata <contyk@redhat.com> - 0.9.43-17
- Forward switch messages to libvirt (#812202)

* Thu Apr 12 2012 Petr Šabata <contyk@redhat.com> - 0.9.43-16
- Don't clear advertise bits on interface up/down (#811422)
- Based on 879e202f0

* Thu Mar 22 2012 Petr Šabata <contyk@redhat.com> - 0.9.43-15
- Don't enable DCB by default in CEE mode (#803482)

* Wed Feb 29 2012 Petr Šabata <contyk@redhat.com> - 0.9.43-14
- Prevent possible segfault due to bad memcpy(), f5ec945 (#796850)

* Wed Jan 04 2012 Petr Šabata <contyk@redhat.com> - 0.9.43-13
- Kill lldpad before starting it (needed for initrd)
- Resolves: rhbz#768555

* Wed Nov 09 2011 Petr Sabata <contyk@redhat.com> - 0.9.43-12
- lldpad: fix core dump (#749943)
- Support for multiple filter info formats (#731407)
- Updating documentation for previous commit (#749057)

* Tue Nov 08 2011 Petr Sabata <contyk@redhat.com> - 0.9.43-11
- lldpad: remain in legacy mode after restart
- Resolves: rhbz#749057

* Wed Oct 12 2011 Petr Sabata <contyk@redhat.com> - 0.9.43-10
- Sync up to da0da5e98
- Reorganize patches a bit, whitespace cleanup
- Resolves: rhbz#733123

* Fri Sep 30 2011 Petr Sabata <contyk@redhat.com> - 0.9.43-9
- Do not send lldp packets if the driver has offloaded dcbx stack
- Resolves: rhbz#741359

* Thu Sep 15 2011 Petr Sabata <contyk@redhat.com> - 0.9.43-8
- Initscript should always check for user's privileges
- Resolves: rhbz#735313

* Tue Aug 30 2011 Petr Sabata <contyk@redhat.com> - 0.9.43-7
- Add new Jens' patch to avoid excessive select() calls
- Resolves: rhbz#694639

* Mon Aug 29 2011 Petr Sabata <contyk@redhat.com> - 0.9.43-6.1
- Minor initscript cleanup, thanks to Petr Pisar for suggestions
- Related: rhbz#683837

* Mon Aug 29 2011 Petr Sabata <contyk@redhat.com> - 0.9.43-6
- Add a custom Red Hat initscript
- Resolves: rhbz#683837

* Fri Aug 26 2011 Petr Sabata <contyk@redhat.com> - 0.9.43-5
- Include recent Open-LLDP bugfixes
- Resolves: rhbz#731407

* Tue Aug 23 2011 Petr Sabata <contyk@redhat.com> - 0.9.43-4
- Include 6.1.z rhbz#694639 fix (thanks to Jens Osterkamp)
- Resolves: rhbz#694639

* Mon Aug 15 2011 Petr Sabata <contyk@redhat.com> - 0.9.43-3
- Fix resource leaks
- Resolves: rhbz#720730
- Resolves: rhbz#728169

* Wed Aug 10 2011 Petr Sabata <contyk@redhat.com> - 0.9.43-2
- Sync up to open-lldp commit 106310e4027e
- Related: rhbz#695943

* Thu Jul 07 2011 Petr Sabata <contyk@redhat.com> - 0.9.43-1
- Update to 0.9.43
- Resolves: rhbz#695943

* Wed May  4 2011 Petr Sabata <psabata@redhat.com> - 0.9.41-5
- Reduce ECP/VDP select timeouts
- Resolves: rhbz#694639

* Mon Apr 11 2011 Petr Sabata <psabata@redhat.com> - 0.9.41-4
- Upstream sync up to 4bf0f2db41be0b282e63646fb6b31f0a938d3865
- Resolves: rhbz#694671
- Resolves: rhbz#694323
- Resolves: rhbz#694925

* Tue Mar 15 2011 Petr Sabata <psabata@redhat.com> - 0.9.41-3
- Including README patch to mention correct open-lldp mailing list
- Related: rhbz#678030

* Mon Mar  7 2011 Petr Sabata <psabata@redhat.com> - 0.9.41-2
- Bugfix patchset from current upstream
- Resolves: rhbz#678030

* Fri Feb  4 2011 Petr Sabata <psabata@redhat.com> - 0.9.41-1
- Rebase to 0.9.41
- Resolves: rhbz#675076

* Wed Feb  2 2011 Petr Sabata <psabata@redhat.com> - 0.9.38-8
- BR cleanup after 0.9.38-7
- Related: rhbz#630087

* Mon Jan 17 2011 Petr Sabata <psabata@redhat.com> - 0.9.38-7
- IEEE 802.1Qbg support
- Resolves: rhbz#630087

* Mon Nov 22 2010 Petr Sabata <psabata@redhat.com> - 0.9.38-6
- lldptool invalid pointer patch
- Resolves: rhbz#647020

* Mon Nov 22 2010 Petr Sabata <psabata@redhat.com> - 0.9.38-5
- Changed devel post and preun sections
- Resolves: rhbz#647833

* Tue Sep 21 2010 Petr Sabata <psabata@redhat.com> - 0.9.38-4
- patch to resolve hang observed during FCoE boot due to dcbx failing to initiate PFC and FCoE app priority negotiations
- Resolves: rhbz#631587

* Fri Jul 30 2010 Jan Zeleny <jzeleny@redhat.com> - 0.9.38-3
- another version of previous fix

* Fri Jul 30 2010 Jan Zeleny <jzeleny@redhat.com> - 0.9.38-2
- lldpad is starting on all runlevels by default (#619605)

* Tue Jun 22 2010 Jan Zeleny <jzeleny@redhat.com> - 0.9.38-1
- rebased to 0.9.38 (various enhancements and bugfixes, see 
  lldpad-0.9.38-relnotes.txt on http://e1000.sf.net for complete list)

* Thu Mar 25 2010 Jan Zeleny <jzeleny@redhat.com> - 0.9.32-2
- added Provides and Obsoletes tags to devel subpackage

* Tue Mar 23 2010 Jan Zeleny <jzeleny@redhat.com> - 0.9.32-1
- rebased to 0.9.32 (various enhancements and bugfixes, see 
  lldpad-0.9.32-relnotes.txt on http://e1000.sf.net for complete list)

* Mon Mar 15 2010 Jan Zeleny <jzeleny@redhat.com> - 0.9.29-2
- minor correction of init script (LSB compliance was broken
  by renaming of the package)

* Mon Mar 15 2010 Jan Zeleny <jzeleny@redhat.com> - 0.9.29-1
- update to 0.9.29 for compatibility with fcoe-utils

* Fri Feb 26 2010 Jan Zeleny <jzeleny@redhat.com> - 0.9.26-2
- updated URL of upstream source tarball

* Thu Feb 25 2010 Jan Zeleny <jzeleny@redhat.com> - 0.9.26-1
- rebased to 0.9.26
- package renamed to lldpad
- enahanced functionality (LLDP supported as well as DCBX)

* Fri Nov 13 2009 Jan Zeleny <jzeleny@redhat.com> - 0.9.19-2
- init script patch adding LSB compliance

* Thu Oct 08 2009 Jan Zeleny <jzeleny@redhat.com> - 0.9.19-1
- update to new upstream version

* Mon Oct 05 2009 Jan Zeleny <jzeleny@redhat.com> - 0.9.15-5
- replaced the last patch, which was not fully functional, with
  the new one

* Wed Sep 09 2009 Karsten Hopp <karsten@redhat.com> 0.9.15-4
- buildrequire libconfig-devel >= 1.3.2, it doesn't build with 1.3.1 due to
  the different config_lookup_string api

* Thu Aug 20 2009 Jan Zeleny <jzeleny@redhat.com> - 0.9.15-3
- update of config_lookup_string() function calls

* Thu Aug 20 2009 Jan Zeleny <jzeleny@redhat.com> - 0.9.15-2
- rebuild in order to match new libconfig

* Mon Aug 17 2009 Jan Zeleny <jzeleny@redhat.com> - 0.9.15-1
- rebase to 0.9.15

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.7-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Fri Mar 20 2009 Jan Zeleny <jzeleny@redhat.com> - 0.9.7-4
- updated scriptlets in spec file to follow the rules

* Wed Mar 11 2009 Jan Zeleny <jzeleny@redhat.com> - 0.9.7-3
- added devel files again to support fcoe-utils package
- added kernel >= 2.6.29 to Requires, deleted dcbnl.h, since it is
  aviable in kernel 2.6.29-rc7
- changed config dir from /etc/sysconfig/dcbd to /etc/dcbd
- updated init script: added mandatory Short description tag,
  deleted default runlevels, which should start the script

* Tue Mar 10 2009 Jan Zeleny <jzeleny@redhat.com> - 0.9.7-2
- added patch to enable usage of libconfig shared in system
- removed devel part of package

* Mon Mar 2 2009 Chris Leech <christopher.leech@intel.com> - 0.9.7-1
- Updated to 0.9.7
- Added a private copy of dcbnl.h until kernel-headers includes it.
  Export patch is making it's way to the upstream kernel via net-2.6,
  expected in 2.6.29-rc7

* Thu Feb 26 2009 Chris Leech <christopher.leech@intel.com> - 0.9.5-1
- initial RPM packaging
