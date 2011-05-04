#!/usr/bin/env ruby


require 'aws'
require 'json'

config = JSON.parse File.open('config.json').read

ec2  = Aws::Ec2.new config['access_key'], config['secret_access_key'], :connection_mode => :per_thread

case ARGV[0]
when 'launch'
  if ARGV[1] == "encoder"
    type = "c1.large"
  else
    type = "t1.tiny"
  end
  instance = ec2.launch_instances config['ami'], :group_ids => config['security_groups'], :key_name => config['ssh_keypair'], :instance_type => type
  puts "Launched"
  puts instance
when 'list'
  ec2.describe_instances.each do |i|
    puts "#{i[:aws_instance_id]} #{i[:dns_name]} #{i[:aws_state]} #{i[:aws_instance_type]}"
  end
when 'terminate'
  ec2.terminate_instances [ARGV[1]]
when 'setup'
  instance_id = ARGV[1]
  instance = ec2.describe_instances.find {|i| i[:aws_instance_id] == instance_id }
  if ARGV[2] == "encoder"
    collector_id = ARGV[3]
    collector = ec2.describe_instances.find {|i| i[:aws_instance_id] == collector_id }
    cmd = "./setupserver.sh %s encoder %s" % [instance[:dns_name], collector[:dns_name]]
    puts "# run"
    puts cmd
  elsif ARGV[2] == "collector"
    cmd = "./setupserver.sh %s collector" % [instance[:dns_name],]
    puts "# run"
    puts cmd
  else
    puts "No such server type"
  end
end

