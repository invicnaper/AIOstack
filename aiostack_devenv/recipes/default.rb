#
# Cookbook Name:: aiostack_devenv
# Recipe:: default
#
# Copyright 2017, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#
include_recipe 'poise-python'

apt_update 'Update the apt cache daily' do
  frequency 86_400
  action :periodic
end

package 'python-dev'
package 'git'

#install psutil
python_package  "psutil"

#install gitpyhton
python_package 'gitpython' 

