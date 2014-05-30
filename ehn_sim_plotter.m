%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%  Script to plot data from our ehn-sim.py simulation
%  Plots energy harvested and battery state vs. time
%  Earvin Caceres, ec2946 & Marina Fahim, mf2895
%  Wireless & Mobile Networking II
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


% get ehn-sim harvesing data in units of mJ
load harvested.dat;                 % read data from harvested.dat
harvestedB_x = harvested(:, 1);      % store x values
harvestedB_x = harvestedB_x ./ 3600;
harvestedB_y = harvested(:, 2);      % store y values

% get ehnants harvesting data in units of microW/cm^2
enhants_x = SetupB_merged_2010_11_3_2010_11_24(2:2001, 1);  % read values from enhants data
enhants_y = SetupB_merged_2010_11_3_2010_11_24(2:2001, 2);  % read values from enhants data

% get battery state data in units of mJ
load batterylog.dat;
battery_x = batterylog(:, 1);
battery_x = battery_x ./ 3600;
battery_y = batterylog(:, 2);

subplot(2,1,1);
plot(battery_x, battery_y);
xlabel('Time (h)');
ylabel('Battery State (mJ)');

subplot(2,1,2);
plot(harvestedB_x, harvestedB_y);
xlabel('Time (h)');
ylabel('Energy Harvested (mJ)');

