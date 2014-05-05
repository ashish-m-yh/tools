#!/usr/bin/perl -w

use strict;

disable_terms();
lock_x();
adduser();

## remove permission from terminal programs
sub disable_terms
{
	my @terms = ('/usr/bin/xterm', '/usr/bin/konsole', '/usr/bin/gnome-terminal');

	foreach my $term (@terms)
	{
		next unless $term;
		chomp $term;
		system("chmod -x $term") if (-e "$term");
	}
}

## Disables X Window user from slipping to console mode or right-click
sub lock_x
{
	open (FH, ">>/etc/X11/Xmodmap") || die $!;	# disable right-click
	print FH "\npointer = 1 2 5 4 3\n";
	close FH;

	open (FH, ">>/etc/X11/xorg.conf") || die $!;	# prevent user from using console
	print FH qq {
Section "ServerFlags"
Option "DontVTSwitch" "true"
Option "DontZap" "true"
Option "DontZoom" "true"
EndSection
	};
	close FH;
}

## create a user which will run the restricted GUI
sub adduser
{
	my $user = 'guest';

	my $passwd_cmd  = `which passwd`;
	chomp $passwd_cmd;

	my $useradd_cmd = `which useradd`;
	chomp $useradd_cmd;

	print "Creating new user ... please provide password";

	`$useradd_cmd -d /home/test $user`;
	`$passwd_cmd $user`;
}
