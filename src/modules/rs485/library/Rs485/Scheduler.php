<?php
// Icinga Rs485 | (c) 2018 Icinga GmbH | GPLv2

namespace Icinga\Module\Rs485;

use Cron\CronExpression;
use ipl\Sql\Connection;
use ipl\Sql\Select;
use React\EventLoop\Factory as Loop;

function datetime_get_time_of_day(\DateTime $dateTime)
{
    $midnight = clone $dateTime;
    $midnight->modify('midnight');

    $diff = $midnight->diff($dateTime);

    return $diff->h * 60 * 60 + $diff->i * 60 + $diff->s;
}

class Scheduler
{
    protected $db;

    protected $loop;

    /** @var array */
    protected $schedules = [];

    /** @var array */
    protected $timers = [];

    public function __construct(Connection $db)
    {
        $this->db = $db;
        $this->loop = Loop::create();
    }

    public function run()
    {
        $updateTimers = function () use (&$updateTimers) {
            $this->updateTimers();

            $this->loop->addTimer(60, $updateTimers);
        };

        $this->loop->futureTick($updateTimers);

        $this->loop->run();
    }

    protected function fetchSchedules()
    {
        $schedules = [];

        $select = (new Select())
            ->from('schedule')
            ->columns('*');

        foreach ($this->db->select($select) as $row) {
            $schedule = (new Schedule())
                ->setId((int) $row->id)
                ->setReportId((int) $row->report_id)
                ->setAction($row->action)
                ->setConfig(\json_decode($row->config, true))
                ->setStart((new \DateTime())->setTimestamp((int) $row->start / 1000))
                ->setFrequency($row->frequency);

            $schedules[$schedule->getChecksum()] = $schedule;
        }

        return $schedules;
    }

    protected function updateTimers()
    {
        $schedules = $this->fetchSchedules();

        $remove = \array_diff_key($this->schedules, $schedules);

        foreach ($remove as $schedule) {
            printf("Removing job %s.\n", "Schedule {$schedule->getId()}");

            $checksum = $schedule->getChecksum();

            if (isset($this->timers[$checksum])) {
                $this->loop->cancelTimer($this->timers[$checksum]);
                unset($this->timers[$checksum]);
            } else {
                printf("Can't find timer for job %s.\n", $checksum);
            }
        }

        $add = \array_diff_key($schedules, $this->schedules);

        foreach ($add as $schedule) {
            $this->add($schedule);
        }

        $this->schedules = $schedules;
    }


    protected function add(Schedule $schedule)
    {
        $name = "Schedule {$schedule->getId()}";
        $frequency = $schedule->getFrequency();
        $start = clone $schedule->getStart();
        $callback = function () use ($schedule) {
            $actionClass = $schedule->getAction();
            /** @var ActionHook $action */
            $action = new $actionClass;

            $action->execute(
                Report::fromDb($schedule->getReportId()),
                $schedule->getConfig()
            );
        };

        switch ($frequency) {
            case 'minutely':
                $modify = '+1 minute';
                break;
            case 'hourly':
                $modify = '+1 hour';
                break;
            case 'daily':
                $modify = '+1 day';
                break;
            case 'weekly':
                $modify = '+1 week';
                break;
            case 'monthly':
                $modify = '+1 month';
                break;
            default:
                throw new \InvalidArgumentException('Invalid frequency.');
        }

        $now = new \DateTime();

        if ($start < $now) {
//            printf("Scheduling job %s to run immediately.\n", $name);
//            $this->loop->futureTick($callback);

            while ($start < $now) {
                $start->modify($modify);
            }
        }

        $next = clone $start;
        $next->modify($modify);
        $interval = $next->getTimestamp() - $start->getTimestamp();

        $current = $start->getTimestamp() - $now->getTimestamp();

        printf("Scheduling job %s to run at %s.\n", $name, $start->format('Y-m-d H:i:s'));

        $loop = function () use (&$loop, $name, $callback, $interval, $schedule) {
            $callback();

            $nextRun = (new \DateTime())
                ->add(new \DateInterval("PT{$interval}S"));

            printf("Scheduling job %s to run at %s.\n", $name, $nextRun->format('Y-m-d H:i:s'));

            $timer = $this->loop->addTimer($interval, $loop);

            $this->timers[$schedule->getChecksum()] = $timer;
        };

        $timer = $this->loop->addTimer($current, $loop);

        $this->timers[$schedule->getChecksum()] = $timer;
    }
}
