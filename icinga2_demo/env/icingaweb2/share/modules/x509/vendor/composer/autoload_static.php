<?php

// autoload_static.php @generated by Composer

namespace Composer\Autoload;

class ComposerStaticInit8c98ed3da38ac69cfc10030dfb826423
{
    public static $prefixLengthsPsr4 = array (
        'l' => 
        array (
            'lipl\\Pagination\\' => 16,
        ),
        'C' => 
        array (
            'Cron\\' => 5,
        ),
    );

    public static $prefixDirsPsr4 = array (
        'lipl\\Pagination\\' => 
        array (
            0 => __DIR__ . '/..' . '/ipl/pagination/src',
        ),
        'Cron\\' => 
        array (
            0 => __DIR__ . '/..' . '/dragonmantank/cron-expression/src/Cron',
        ),
    );

    public static $classMap = array (
        'Composer\\InstalledVersions' => __DIR__ . '/..' . '/composer/InstalledVersions.php',
    );

    public static function getInitializer(ClassLoader $loader)
    {
        return \Closure::bind(function () use ($loader) {
            $loader->prefixLengthsPsr4 = ComposerStaticInit8c98ed3da38ac69cfc10030dfb826423::$prefixLengthsPsr4;
            $loader->prefixDirsPsr4 = ComposerStaticInit8c98ed3da38ac69cfc10030dfb826423::$prefixDirsPsr4;
            $loader->classMap = ComposerStaticInit8c98ed3da38ac69cfc10030dfb826423::$classMap;

        }, null, ClassLoader::class);
    }
}
