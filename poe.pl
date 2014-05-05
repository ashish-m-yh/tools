#!/usr/bin/perl

use strict;

sub BEGIN {
unshift (@INC, '/home/admin/perl_modules/lib/site_perl/5.005/i386-linux');
unshift (@INC, '/home/admin/perl_modules/lib/site_perl/5.005');
open FH, ">success.log";
};

$SIG{SEGV} = $SIG{TERM} = $SIG{DIE} = $SIG{INT} = $SIG{KILL} = \&finish();

use HTTP::Request;
use POE qw(Component::Client::HTTP);
use Time::HiRes qw(time);

$|++;

POE::Component::Client::HTTP->spawn(Agent => 'My UA', Alias => 'ua');

my %requests;
my $start_time = 0;
my $end_time = 0;
my $count = 0;
my $sec = 0;

my @latency;
my $begin_time = time;
my $total_req  = 0;
my $success = 0;
my $id = 0;

sub got_response
{
    my ($heap, $request_packet, $response_packet) = @_[ HEAP, ARG0, ARG1 ];

    my $http_request  = $request_packet->[0];
    my $http_response = $response_packet->[0];

    if (defined $http_response)
    {
        my $response_string = $http_response->as_string();
        $response_string =~ s/^/| /mg;

        my $httpurl    = $http_request->uri;
        my ($urlid) = $httpurl =~ /urlarrayid=(.*)/;

        $latency[$urlid]->[1] = time;
        $latency[$urlid]->[2] = $httpurl;

        if ($http_response->is_success)
        {
             ++$success;
        } else
        {
             print FH $response_string,"\n";
        }
    }
}

sub _start
{
    my $kernel = $_[KERNEL];

    my @url_list = @{$requests{$sec}};

    foreach my $url (@url_list)
    {
        ++$total_req;
        ++$id;

        if ($url =~ /\?/)
        {
#               $url .= "&urlarrayid=$id";
        } else {
#               $url .= "?urlarrayid=$id";
        }

        $latency[$id]->[0] = time;

        my $request = HTTP::Request->new('GET', $url);
        $kernel->post("ua" => "request", "got_response", $request);
    }
}

sub createSession
{
        eval {
                POE::Session->create(package_states => [ main => [ "_start", "got_response" ] ]);
        };
}

my @times;

sub readLog
{
        use Time::Local qw(timelocal);

        while (<STDIN>)
        {
                chomp;

                my ($time, $uri) = split(/\t/);

                eval {
                my ($year, $mon, $mday, $hours, $min, $sec) = $time =~ /(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})/;
                my $unixtime = timelocal($sec,$min,$hours,$mday,$mon,$year);
                $start_time ||= $unixtime;
                $end_time = $unixtime;

                push (@{$requests{$unixtime}}, "http://202.138.124.162:8080$uri");
                };
        }

        # @times is a sorted list of %requests keys.
        @times = sort { $a <=> $b } keys %requests;
}

sub loadGenerator
{
  # Please excuse the indenting.
  POE::Session->create(
    inline_states => {
      _start => sub {
        my ($kernel, $heap) = @_[KERNEL, HEAP];

        $kernel->yield("create_some_more");
      },

      create_some_more => sub {
        my ($kernel, $heap) = @_[KERNEL, HEAP];

        # Pull the next $unixtime off the list of times.
        $sec = shift @times;

        # If we ran out of times, we're done!
        return unless defined $sec;

        # Create a session to process that time.  Note:
        # createSession() uses $sec internally to determine which URIs
        # to visit.
        createSession();

        # We're finished if there are no more times.
        return unless @times;

        # More times.  Wait for the next one.  $times[0] - $sec is the
        # amount of time until the next item in @times.
        $kernel->delay( create_some_more => $times[0] - $sec );
      },
    }
  );
}

readLog();
loadGenerator();
$poe_kernel->run();

sub finish
{
        eval {
                open (FILE, ">report.log");
                select FILE;

                my $thruput = sprintf("%0.2f", $total_req/(time - $begin_time));
                print "Total requests: $total_req req\n";
                print "Throughput: $thruput req/sec\n";
                print "Success rate: ", $success/$total_req*100,"%\n";
                print "Latency:\n";

                my $sum = 0;

                foreach (@latency)
                {
                        next unless ref $_;

                        my $url = $_->[2];

                        $_ = sprintf("%0.2f", $_->[1] - $_->[0]);
                        print $_," sec\t$url\n";

                        $sum += $_ if ($_ > 0);
                }

                print "Average Latency: ";
                print sprintf("%0.2f",  $sum/$#latency)," sec/req\n";
                close FILE;
        };
}

sub END {
        close FH;
        finish();
}
