#!/usr/bin/env ruby


require 'aws'
require 'json'

config = JSON.parse File.open('config.json').read

ec2  = Aws::Ec2.new config['access_key'], config['secret_access_key'], :connection_mode => :per_thread

case ARGV[0]
when 'launch'
  instance = ec2.launch_instances config['ami'], :group_ids => config['security_groups'], :key_name => config['ssh_keypair'], :instance_type => config['instance_type']
  puts "Launched"
  puts instance
when 'list'
  ec2.describe_instances.each do |i|
    puts "#{i[:aws_instance_id]} #{i[:dns_name]} #{i[:aws_state]}"
  end
when 'terminate'
  ec2.terminate_instances [ARGV[1]]
when 'setup'
  instance_id = ARGV[1]
  instance = ec2.describe_instances.find {|i| i[:aws_instance_id] == instance_id }
  ENV['HOSTS']=instance[:dns_name]
  `cap setup`
end

